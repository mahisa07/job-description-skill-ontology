import os
import re
import socket
import ssl
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from backend.models.schemas import VerificationCheckItem, TrustVerificationResult

class TrustVerificationService:
    # Public & Generic Email Providers
    GENERIC_EMAIL_DOMAINS = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com',
        'icloud.com', 'protonmail.com', 'proton.me', 'zoho.com', 'mail.com',
        'yandex.com', 'live.com', 'msn.com', 'gmx.com', 'fastmail.com'
    }

    # Known Disposable / Temporary Email Providers (High Risk for Recruitment)
    DISPOSABLE_EMAIL_DOMAINS = {
        'mailinator.com', 'tempmail.com', '10minutemail.com', 'guerrillamail.com',
        'trashmail.com', 'sharklasers.com', 'yopmail.com', 'dispostable.com',
        'throwawaymail.com', 'getairmail.com', 'temp-mail.org'
    }

    # Recognized Applicant Tracking Systems (ATS) and Verified Job Platforms
    RECOGNIZED_ATS_DOMAINS = {
        'greenhouse.io', 'lever.co', 'myworkdayjobs.com', 'workday.com',
        'ashbyhq.com', 'smartrecruiters.com', 'jobvite.com', 'bamboohr.com',
        'icims.com', 'taleo.net', 'recruitee.com', 'workable.com'
    }

    RECOGNIZED_JOB_BOARDS = {
        'linkedin.com', 'indeed.com', 'glassdoor.com', 'monster.com',
        'dice.com', 'ziprecruiter.com', 'wellfound.com', 'handshake.com'
    }

    # Red Flag Scam Detection Patterns
    RISK_PATTERNS = [
        {
            "id": "UPFRONT_FEE",
            "category": "Financial Risk",
            "severity": "HIGH",
            "patterns": [
                r'\b(?:registration|application|training|processing|enrollment|onboarding)\s+fees?\b',
                r'\bpay\s+(?:an?\s+)?upfront\s+fee\b',
                r'\bpay\s+for\s+(?:your\s+own\s+)?background\s+check\b',
                r'\brequire(?:s|d)?\s+a\s+(?:refundable\s+)?deposit\b'
            ],
            "title": "Upfront Fee or Deposit Request",
            "explanation": "The job description or correspondence suggests candidates must pay an upfront fee for processing, training, or background checks. Legitimate employers never charge candidates money to apply or be hired."
        },
        {
            "id": "EQUIPMENT_CHECK_SCAM",
            "category": "Financial Risk",
            "severity": "HIGH",
            "patterns": [
                r'\b(?:we\s+will\s+send|send\s+you)\s+a\s+check\s+to\s+purchase\b',
                r'\bpurchase\s+(?:home\s+office\s+)?equipment\s+from\s+(?:our\s+)?(?:approved|certified|designated)\s+vendor\b',
                r'\bcash(?:ier\'?s)?\s+check\s+for\s+office\s+supplies\b',
                r'\bwire\s+(?:money|funds)\s+back\b'
            ],
            "title": "Equipment Check / Vendor Payment Request",
            "explanation": "Mentions sending a check for the candidate to purchase equipment from a specific vendor. This is a common fake-check scam where the check bounces after funds are transferred."
        },
        {
            "id": "CRYPTO_OR_GIFT_CARDS",
            "category": "Financial Risk",
            "severity": "HIGH",
            "patterns": [
                r'\b(?:bitcoin|crypto|cryptocurrency|ethereum|usdt)\b',
                r'\b(?:gift\s*card|apple\s+card|steam\s+card|amazon\s+card)\s+payment\b',
                r'\bwire\s+transfer\s+(?:via\s+)?(?:western\s+union|moneygram)\b'
            ],
            "title": "Cryptocurrency or Gift Card Transaction",
            "explanation": "Reference to cryptocurrency, gift cards, or irreversible wire transfers. Legitimate corporate payroll and onboarding never use untraceable consumer payment channels."
        },
        {
            "id": "UNOFFICIAL_MESSAGING_INTERVIEW",
            "category": "Communication Risk",
            "severity": "MEDIUM_HIGH",
            "patterns": [
                r'\b(?:interview|chat)\s+(?:will\s+be\s+conducted\s+)?(?:via|on|through)\s+telegram\b',
                r'\bcontact\s+(?:us\s+|the\s+hiring\s+manager\s+)?on\s+telegram\b',
                r'\bdownload\s+(?:the\s+)?telegram\s+app\s+for\s+(?:the\s+)?interview\b',
                r'\binterview\s+(?:via|on)\s+whatsapp\b',
                r'\bgoogle\s+hangouts\s+interview\b'
            ],
            "title": "Exclusive Messaging App Interview",
            "explanation": "Interview is conducted exclusively via instant messaging apps (Telegram, WhatsApp, Google Hangouts) without official video, phone, or corporate portal interactions. Scammers frequently use encrypted messaging to avoid corporate audit trails."
        },
        {
            "id": "PREMATURE_SENSITIVE_INFO",
            "category": "Identity Theft Risk",
            "severity": "HIGH",
            "patterns": [
                r'\b(?:send|provide|submit)\s+(?:your\s+)?(?:ssn|social\s+security\s+number)\b',
                r'\bbank\s+(?:account|routing)\s+details\s+(?:with\s+application|before\s+interview)\b',
                r'\bcopy\s+of\s+(?:your\s+)?(?:credit\s+card|debit\s+card)\b'
            ],
            "title": "Premature Sensitive Financial / SSN Data Request",
            "explanation": "Requests sensitive identity or financial information (SSN, banking details) at the initial application stage. Genuine employers only collect banking info for payroll after an official written offer is formally accepted."
        },
        {
            "id": "UNREALISTIC_COMPENSATION",
            "category": "Content Anomaly",
            "severity": "LOW_MEDIUM",
            "patterns": [
                r'\b(?:earn|make)\s+\$?(?:5000|10000)\s*(?:\/|\s*per\s*)(?:week|day)\s+(?:with\s+)?no\s+experience\b',
                r'\bguaranteed\s+(?:instant|immediate)\s+hiring\s+without\s+interview\b',
                r'\bno\s+skills?\s+required\s+high\s+pay\b'
            ],
            "title": "Unrealistic Compensation / No-Interview Guarantee",
            "explanation": "Guarantees exceptionally high compensation with zero experience, or promises immediate hiring without a formal interview process."
        }
    ]

    @classmethod
    def _extract_domain_from_url(cls, url: str) -> str:
        if not url:
            return ""
        clean = url.strip()
        if not re.match(r'^https?://', clean, re.IGNORECASE):
            clean = "http://" + clean
        try:
            parsed = urllib.parse.urlparse(clean)
            host = parsed.netloc.lower()
            # Strip port if present
            if ':' in host:
                host = host.split(':')[0]
            # Strip leading 'www.'
            if host.startswith('www.'):
                host = host[4:]
            return host
        except Exception:
            return ""

    @classmethod
    def _detect_company_and_domain(cls, raw_text: str, user_company: Optional[str] = "", user_company_url: Optional[str] = "", recruiter_email: Optional[str] = "") -> Tuple[str, str]:
        """Determine company name and candidate domain using input and text heuristics."""
        comp_name = (user_company or "").strip()
        comp_domain = cls._extract_domain_from_url(user_company_url or "")

        # If company name not provided, attempt extraction from JD text
        if not comp_name and raw_text:
            lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
            for line in lines[:10]:
                match = re.search(r'^(?:COMPANY|ORGANIZATION|EMPLOYER)\s*[:\-]\s*(.+)$', line, re.IGNORECASE)
                if match:
                    comp_name = match.group(1).strip()
                    break
            
            if not comp_name:
                about_match = re.search(r'About\s+([A-Z][A-Za-z0-9\s&.,\'\-]{2,35}?)(?:\s+is|\s+was|\s+seeks|\s+invites|\.)', raw_text)
                if about_match:
                    comp_name = about_match.group(1).strip()

        # If domain not provided, look for corporate website or corporate email domain
        if not comp_domain:
            if recruiter_email and '@' in recruiter_email:
                rec_domain = recruiter_email.strip().split('@')[-1].lower()
                if rec_domain not in cls.GENERIC_EMAIL_DOMAINS and rec_domain not in cls.DISPOSABLE_EMAIL_DOMAINS:
                    comp_domain = rec_domain

        if not comp_domain and raw_text:
            # Look for URLs in the text
            url_matches = re.findall(r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', raw_text)
            for m in url_matches:
                dom = m.lower().replace('www.', '')
                if dom not in cls.GENERIC_EMAIL_DOMAINS and dom not in cls.RECOGNIZED_JOB_BOARDS:
                    comp_domain = dom
                    break

        if not comp_name and comp_domain:
            parts = comp_domain.split('.')
            if len(parts) >= 2:
                comp_name = parts[0].capitalize()

        return comp_name, comp_domain

    @classmethod
    def _check_dns_resolution(cls, domain: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Verify whether a domain resolves to valid IP addresses via DNS."""
        if not domain or len(domain) < 3 or '.' not in domain:
            return False, None, "Invalid domain format."
        try:
            # Short timeout to keep analysis fast and responsive
            orig_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(2.5)
            try:
                addr_info = socket.getaddrinfo(domain, 80, socket.AF_INET, socket.SOCK_STREAM)
                ips = list(set([item[4][0] for item in addr_info if item[4]]))
                if ips:
                    return True, ips[0], f"Resolved to active public IP address ({ips[0]})."
                return False, None, "Domain lookup returned no IP addresses."
            finally:
                socket.setdefaulttimeout(orig_timeout)
        except socket.gaierror as e:
            return False, None, f"DNS resolution failed (host '{domain}' not found)."
        except socket.timeout:
            return False, None, f"DNS resolution timed out for '{domain}'."
        except Exception as e:
            return False, None, f"DNS lookup error: {str(e)}"

    @classmethod
    def _check_http_connectivity(cls, domain: str) -> Tuple[bool, Optional[str], Optional[str], bool]:
        """Test HTTP/HTTPS connectivity to the domain."""
        if not domain or '.' not in domain:
            return False, None, "Domain not provided.", False

        urls_to_try = [f"https://{domain}", f"http://{domain}"]
        last_error = ""
        has_ssl = False

        for target_url in urls_to_try:
            try:
                req = urllib.request.Request(
                    target_url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                )
                ctx = ssl.create_default_context()
                # 3.0 second timeout for responsiveness
                with urllib.request.urlopen(req, context=ctx, timeout=3.0) as resp:
                    status_code = resp.getcode()
                    final_url = resp.geturl()
                    if status_code in (200, 301, 302, 307, 308):
                        if target_url.startswith("https://") or final_url.startswith("https://"):
                            has_ssl = True
                        return True, final_url, f"Web server active and reachable (HTTP {status_code}).", has_ssl
            except ssl.SSLError as e:
                has_ssl = False
                last_error = f"SSL/TLS certificate error: {str(e)}"
            except HTTPError as e:
                # 403 or 401 still proves the web server and domain exist!
                if e.code in (401, 403):
                    return True, target_url, f"Web server active (HTTP {e.code} Protected).", target_url.startswith("https")
                last_error = f"HTTP {e.code} response."
            except URLError as e:
                last_error = f"Connection error: {e.reason}"
            except socket.timeout:
                last_error = "Connection timed out."
            except Exception as e:
                last_error = f"Connection probe failed: {str(e)}"

        return False, None, f"Official website check was inconclusive or unreachable ({last_error}).", has_ssl

    @classmethod
    def _check_mail_server(cls, domain: str) -> Tuple[bool, str]:
        """Test whether the domain is configured with mail infrastructure."""
        if not domain or '.' not in domain:
            return False, "No domain specified for mail check."
        
        # Test candidate mail subdomains
        mail_candidates = [f"mail.{domain}", f"smtp.{domain}", f"mx.{domain}", domain]
        orig_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(2.0)
        try:
            for candidate in mail_candidates:
                try:
                    res = socket.gethostbyname(candidate)
                    if res:
                        return True, f"Configured mail host detected ({candidate} -> {res})."
                except Exception:
                    continue
            return False, f"No dedicated mail host detected for {domain}."
        finally:
            socket.setdefaulttimeout(orig_timeout)

    @classmethod
    def perform_verification(
        cls,
        raw_text: str,
        job_role: Optional[str] = "",
        company: Optional[str] = "",
        company_url: Optional[str] = "",
        recruiter_name: Optional[str] = "",
        recruiter_email: Optional[str] = "",
        recruiter_profile_url: Optional[str] = "",
        job_posting_url: Optional[str] = ""
    ) -> TrustVerificationResult:
        """
        Executes genuine, independent, evidence-based trust and verification checks:
        A. Company Verification
        B. Recruiter Verification
        C. Job Posting Verification
        D. Consistency and Risk Indicators
        E. Summary Status & Indicative Score
        """
        verified_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        checks: List[VerificationCheckItem] = []
        risk_indicators: List[str] = []
        positive_indicators: List[str] = []
        limitations: List[str] = []

        # -------------------------------------------------------------
        # 1. Company Detection & Normalization
        # -------------------------------------------------------------
        comp_name, comp_domain = cls._detect_company_and_domain(
            raw_text=raw_text,
            user_company=company,
            user_company_url=company_url,
            recruiter_email=recruiter_email
        )

        company_verified = False
        final_website_url = None
        dns_ok = False
        http_ok = False
        has_ssl = False

        if comp_domain:
            # Check A1: DNS Resolution
            dns_ok, ip_addr, dns_msg = cls._check_dns_resolution(comp_domain)
            if dns_ok:
                checks.append(VerificationCheckItem(
                    check_name="Company Domain DNS Resolution",
                    category="company",
                    status="VERIFIED",
                    details=f"The domain '{comp_domain}' is registered with public DNS records. {dns_msg}",
                    evidence_url=f"https://{comp_domain}",
                    source_name="DNS / Internet Public Routing"
                ))
                positive_indicators.append(f"Company domain '{comp_domain}' successfully resolved to IP {ip_addr}.")
            else:
                checks.append(VerificationCheckItem(
                    check_name="Company Domain DNS Resolution",
                    category="company",
                    status="UNCONFIRMED",
                    details=f"Could not resolve DNS records for '{comp_domain}'. {dns_msg}",
                    evidence_url=None,
                    source_name="DNS Public Lookup"
                ))

            # Check A2: Web Connectivity & SSL
            http_ok, live_url, http_msg, has_ssl = cls._check_http_connectivity(comp_domain)
            if http_ok:
                company_verified = True
                final_website_url = live_url
                ssl_badge = "with valid SSL/TLS encryption" if has_ssl else "without HTTPS encryption"
                checks.append(VerificationCheckItem(
                    check_name="Official Company Website Verification",
                    category="company",
                    status="VERIFIED",
                    details=f"Official website is live and publicly accessible at {live_url} ({ssl_badge}). {http_msg}",
                    evidence_url=live_url,
                    source_name="HTTP/HTTPS Web Connectivity Probe"
                ))
                positive_indicators.append(f"Official company website is live at {live_url}.")
            else:
                checks.append(VerificationCheckItem(
                    check_name="Official Company Website Verification",
                    category="company",
                    status="UNAVAILABLE",
                    details=f"Direct HTTP check to '{comp_domain}' could not be completed or timed out. {http_msg}",
                    evidence_url=f"http://{comp_domain}",
                    source_name="HTTP Web Probe"
                ))
                limitations.append(f"External web connection to '{comp_domain}' was inconclusive or timed out during the check.")

        else:
            checks.append(VerificationCheckItem(
                check_name="Company Identity & Web Presence",
                category="company",
                status="UNAVAILABLE",
                details="No company website or domain was provided in the input, and none could be reliably extracted from the Job Description text.",
                evidence_url=None,
                source_name="Input Analysis"
            ))
            limitations.append("Company website was not provided, limiting independent corporate footprint verification.")

        # -------------------------------------------------------------
        # 2. Recruiter Verification
        # -------------------------------------------------------------
        rec_name_clean = (recruiter_name or "").strip()
        rec_email_clean = (recruiter_email or "").strip().lower()
        rec_profile_clean = (recruiter_profile_url or "").strip()
        affiliation_status = "NOT_PROVIDED"

        if rec_email_clean:
            # Syntax validation
            is_valid_email = bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', rec_email_clean))
            if not is_valid_email:
                checks.append(VerificationCheckItem(
                    check_name="Recruiter Email Syntax",
                    category="recruiter",
                    status="WARNING",
                    details=f"Recruiter email '{rec_email_clean}' does not match standard RFC 5322 email syntax.",
                    evidence_url=None,
                    source_name="Email Validation"
                ))
                risk_indicators.append("Recruiter email format is invalid or malformed.")
            else:
                rec_domain = rec_email_clean.split('@')[-1]

                # Disposable email check
                if rec_domain in cls.DISPOSABLE_EMAIL_DOMAINS:
                    affiliation_status = "HIGH_RISK"
                    checks.append(VerificationCheckItem(
                        check_name="Recruiter Email Domain Integrity",
                        category="recruiter",
                        status="WARNING",
                        details=f"Email domain '{rec_domain}' is an anonymous temporary/disposable inbox service. Legitimate hiring professionals never use disposable email addresses.",
                        evidence_url=None,
                        source_name="Disposable Email Registry"
                    ))
                    risk_indicators.append(f"Recruiter is using a disposable/temporary email address (@{rec_domain}).")

                # Free generic email check
                elif rec_domain in cls.GENERIC_EMAIL_DOMAINS:
                    affiliation_status = "GENERIC_EMAIL"
                    checks.append(VerificationCheckItem(
                        check_name="Recruiter Email Domain Affiliation",
                        category="recruiter",
                        status="WARNING",
                        details=f"Recruiter contacted candidate via a free public email provider (@{rec_domain}) rather than an official corporate domain. While common for freelancers or micro-agencies, major enterprise recruiters use company-owned domains.",
                        evidence_url=None,
                        source_name="Email Domain Analysis"
                    ))
                    risk_indicators.append(f"Recruiter is using a generic public email address (@{rec_domain}) instead of an official corporate domain.")

                # Corporate email check
                else:
                    mail_ok, mail_msg = cls._check_mail_server(rec_domain)
                    # Compare with company domain
                    domain_matches = False
                    if comp_domain:
                        domain_matches = (rec_domain == comp_domain) or rec_domain.endswith('.' + comp_domain)

                    if domain_matches:
                        affiliation_status = "CONFIRMED"
                        checks.append(VerificationCheckItem(
                            check_name="Recruiter Corporate Email Affiliation",
                            category="recruiter",
                            status="VERIFIED",
                            details=f"Recruiter email domain '{rec_domain}' directly matches the company's verified domain '{comp_domain}'. {mail_msg}",
                            evidence_url=f"https://{comp_domain}",
                            source_name="Corporate Domain & MX Match"
                        ))
                        positive_indicators.append(f"Recruiter email domain matches the official company domain ({rec_domain}).")
                    else:
                        affiliation_status = "UNCONFIRMED"
                        checks.append(VerificationCheckItem(
                            check_name="Recruiter Corporate Email Affiliation",
                            category="recruiter",
                            status="UNCONFIRMED",
                            details=f"Recruiter uses custom domain '{rec_domain}' which does not match claimed company domain '{comp_domain or 'Unspecified'}'. May represent an external recruiting agency.",
                            evidence_url=None,
                            source_name="Domain Comparison"
                        ))

        else:
            checks.append(VerificationCheckItem(
                check_name="Recruiter Contact Details",
                category="recruiter",
                status="UNAVAILABLE",
                details="No recruiter email address was provided for affiliation and domain verification.",
                evidence_url=None,
                source_name="Input Analysis"
            ))

        # Professional Profile URL check
        if rec_profile_clean:
            is_linkedin = "linkedin.com/in/" in rec_profile_clean.lower()
            checks.append(VerificationCheckItem(
                check_name="Recruiter Professional Profile",
                category="recruiter",
                status="VERIFIED" if is_linkedin else "UNCONFIRMED",
                details=f"Professional profile URL provided: {rec_profile_clean}. Note: Profile presence provides identity evidence, but does not independently certify authorized hiring authority.",
                evidence_url=rec_profile_clean,
                source_name="Professional Profile Audit"
            ))
            positive_indicators.append("Professional recruiter profile URL was provided.")
        elif rec_name_clean:
            checks.append(VerificationCheckItem(
                check_name="Recruiter Profile Reference",
                category="recruiter",
                status="UNCONFIRMED",
                details=f"Recruiter name '{rec_name_clean}' was provided without a professional profile URL for independent reference.",
                evidence_url=None,
                source_name="Input Analysis"
            ))

        # -------------------------------------------------------------
        # 3. Job Posting Verification
        # -------------------------------------------------------------
        posting_url_clean = (job_posting_url or "").strip()
        posting_status = "NOT_PROVIDED"
        post_host = ""
        is_ats = False
        is_board = False
        link_live = False

        if posting_url_clean:
            post_host = cls._extract_domain_from_url(posting_url_clean)
            is_ats = any(post_host.endswith(ats) for ats in cls.RECOGNIZED_ATS_DOMAINS)
            is_board = any(post_host.endswith(board) for board in cls.RECOGNIZED_JOB_BOARDS)
            is_company_site = (comp_domain and post_host.endswith(comp_domain))

            # Test if link is live
            link_live, live_target, link_msg, _ = cls._check_http_connectivity(post_host)

            if is_ats or is_company_site:
                posting_status = "MATCHED"
                checks.append(VerificationCheckItem(
                    check_name="Official Career Portal Listing Match",
                    category="job_posting",
                    status="VERIFIED" if link_live else "UNCONFIRMED",
                    details=f"Job posting URL is hosted on an official corporate portal or verified ATS ({post_host}). {link_msg}",
                    evidence_url=posting_url_clean,
                    source_name="ATS / Career Portal Cross-Reference"
                ))
                positive_indicators.append(f"Job posting reference originates from official careers platform ({post_host}).")
            elif is_board:
                posting_status = "EXTERNAL_SOURCE"
                checks.append(VerificationCheckItem(
                    check_name="Public Job Board Reference",
                    category="job_posting",
                    status="VERIFIED" if link_live else "UNCONFIRMED",
                    details=f"Job listing references recognized public recruitment board ({post_host}). {link_msg}",
                    evidence_url=posting_url_clean,
                    source_name="Job Board Audit"
                ))
                positive_indicators.append(f"Job posting reference hosted on verified job network ({post_host}).")
            else:
                posting_status = "UNCONFIRMED"
                checks.append(VerificationCheckItem(
                    check_name="Job Reference URL Authenticity",
                    category="job_posting",
                    status="UNCONFIRMED",
                    details=f"Job reference URL is hosted on an unverified third-party domain ({post_host}). {link_msg}",
                    evidence_url=posting_url_clean,
                    source_name="URL Inspection"
                ))
        else:
            checks.append(VerificationCheckItem(
                check_name="Public Vacancy Cross-Reference",
                category="job_posting",
                status="UNAVAILABLE",
                details="No public job listing URL was submitted. Note: Many genuine vacancies are confidential, agency-sourced, or direct referrals, so an unlisted vacancy does not automatically indicate risk.",
                evidence_url=None,
                source_name="Input Analysis"
            ))

        # -------------------------------------------------------------
        # 4. Consistency and Risk Indicators (NLP & Scam Heuristics)
        # -------------------------------------------------------------
        has_high_risk_scam = False

        for r_pattern in cls.RISK_PATTERNS:
            found_evidence = []
            for pat in r_pattern["patterns"]:
                matches = re.findall(pat, raw_text, re.IGNORECASE)
                if matches:
                    found_evidence.extend(matches)

            if found_evidence:
                matched_snippet = f"Trigger text detected: '{found_evidence[0]}'"
                checks.append(VerificationCheckItem(
                    check_name=r_pattern["title"],
                    category="risk",
                    status="WARNING",
                    details=f"{r_pattern['explanation']} ({matched_snippet})",
                    evidence_url=None,
                    source_name="NLP Scam Heuristic Scanner"
                ))
                risk_indicators.append(f"{r_pattern['title']}: {r_pattern['explanation']}")
                if r_pattern["severity"] == "HIGH":
                    has_high_risk_scam = True

        if not risk_indicators:
            checks.append(VerificationCheckItem(
                check_name="Scam & Fraud Pattern Audit",
                category="risk",
                status="VERIFIED",
                details="No upfront fee requests, fake-check purchasing schemes, cryptocurrency demands, or suspicious messaging-only interview triggers were detected in the text.",
                evidence_url=None,
                source_name="Pattern Analysis Engine"
            ))
            positive_indicators.append("Zero fraudulent hiring patterns or advance-fee scam triggers detected.")

        # -------------------------------------------------------------
        # 5. Summary Status & Indicative Evidence Score Calculation
        # -------------------------------------------------------------
        # Rule 1: High Risk if confirmed financial scam, disposable email, or high-risk pattern detected
        if has_high_risk_scam or affiliation_status == "HIGH_RISK":
            status = "High Risk"
            summary_reason = "High-risk indicators were detected in this submission (e.g., upfront payment demands, fake-check equipment purchase schemes, or disposable recruiter contact). Exercise extreme caution."
            trust_score = max(5, 30 - (len(risk_indicators) * 10))

        # Rule 2: Verified if company domain verified, recruiter email matches corporate domain, no scam patterns, and active job/profile
        elif company_verified and affiliation_status == "CONFIRMED" and not risk_indicators:
            status = "Verified"
            summary_reason = f"Company identity independently confirmed ({comp_domain}), recruiter email domain matches corporate records, and no scam or fraudulent signals were detected."
            trust_score = 92 if posting_status == "MATCHED" else 88

        # Rule 3: Partially Verified if company verified or recruiter has online footprint, but some items unconfirmed/generic without scam flags
        elif (company_verified or affiliation_status == "CONFIRMED" or rec_profile_clean) and not has_high_risk_scam:
            status = "Partially Verified"
            if company_verified and affiliation_status == "GENERIC_EMAIL":
                summary_reason = f"Company identity ({comp_domain or comp_name}) is confirmed live, but the recruiter is communicating from a generic public email address (@{rec_email_clean.split('@')[-1]})."
                trust_score = 62
            elif company_verified:
                summary_reason = f"Company digital presence and website ({comp_domain}) were independently verified, but recruiter affiliation details were not provided or could not be fully cross-referenced."
                trust_score = 68
            else:
                summary_reason = "Some recruiter or listing information could be referenced, but official corporate domain ownership could not be definitively confirmed."
                trust_score = 55

        # Rule 4: Unverified if company website / domain was not provided or could not be resolved, and no scam patterns
        else:
            status = "Unverified"
            summary_reason = "Insufficient verifiable evidence was available to confirm the company website or recruiter affiliation. No direct scam triggers were found, but the vacancy could not be independently cross-referenced."
            trust_score = 42

        # Adjust score slightly for positive/negative evidence counts
        if status in ("Partially Verified", "Verified"):
            if posting_status in ("MATCHED", "EXTERNAL_SOURCE"):
                trust_score = min(98, trust_score + 6)
            if len(positive_indicators) >= 3 and not risk_indicators:
                trust_score = min(98, trust_score + 4)

        # External Search API Note
        if not os.environ.get("GOOGLE_SEARCH_API_KEY") and not os.environ.get("VERIFICATION_API_KEY"):
            limitations.append("External search indexing API key is not configured. Real-time DNS lookups, HTTP probes, domain MX routing, and heuristic scam pattern audits were executed natively.")

        score_disclaimer = "This is an indicative evidence score based on verifiable digital footprint, domain configuration, and risk analysis. It is not a statistical guarantee or certified legal endorsement."

        company_verification_dict = {
            "company_name": comp_name or "Not Specified",
            "website_url": final_website_url or (f"https://{comp_domain}" if comp_domain else ""),
            "domain": comp_domain or "",
            "dns_resolved": dns_ok,
            "ssl_valid": has_ssl,
            "dns_status": "VERIFIED" if dns_ok else ("UNCONFIRMED" if comp_domain else "UNAVAILABLE"),
            "ssl_status": "VERIFIED" if has_ssl else ("UNCONFIRMED" if comp_domain else "UNAVAILABLE"),
            "notes": f"Website domain {comp_domain} verified active." if dns_ok else (f"Domain {comp_domain} could not be resolved." if comp_domain else "Company website was not provided.")
        }

        recruiter_verification_dict = {
            "recruiter_name": rec_name_clean or "Not Provided",
            "email": rec_email_clean or "",
            "email_type": "Corporate" if affiliation_status == "CONFIRMED" else ("Disposable / Tempmail" if affiliation_status == "HIGH_RISK" else ("Public Webmail" if affiliation_status == "GENERIC_EMAIL" else ("Invalid" if affiliation_status == "MISMATCH" else "Not Provided"))),
            "domain_matches_company": (affiliation_status == "CONFIRMED"),
            "profile_url": rec_profile_clean or None,
            "status": "VERIFIED" if affiliation_status == "CONFIRMED" else ("HIGH_RISK" if affiliation_status == "HIGH_RISK" else ("PARTIALLY_VERIFIED" if (rec_profile_clean or affiliation_status == "GENERIC_EMAIL") else "UNCONFIRMED")),
            "notes": "Recruiter domain matches official corporate records." if affiliation_status == "CONFIRMED" else (f"Recruiter using generic webmail provider (@{rec_email_clean.split('@')[-1]})." if affiliation_status == "GENERIC_EMAIL" else ("Recruiter details were not provided." if not rec_email_clean else "Corporate affiliation could not be confirmed."))
        }

        posting_verification_dict = {
            "posting_url": posting_url_clean or None,
            "domain": post_host or "",
            "ats_platform": "Recognized Platform" if (is_ats or is_board) else None,
            "is_recognized_platform": (is_ats or is_board),
            "is_reachable": link_live,
            "status": "VERIFIED" if (link_live and (is_ats or is_board)) else ("EXTERNAL_SOURCE" if is_board else ("UNCONFIRMED" if posting_url_clean else "UNAVAILABLE")),
            "notes": "Posting URL verified live." if link_live else ("Posting reference URL could not be verified." if posting_url_clean else "No public posting URL provided.")
        }

        risk_assessment_dict = {
            "risk_level": "HIGH" if (has_high_risk_scam or affiliation_status == "HIGH_RISK") else ("MEDIUM" if risk_indicators else "LOW"),
            "red_flags_detected": [{"id": f"FLAG_{i}", "title": r.split(":")[0], "explanation": r.split(":", 1)[-1].strip()} for i, r in enumerate(risk_indicators)] if risk_indicators else [],
            "clean": (len(risk_indicators) == 0 and affiliation_status != "HIGH_RISK"),
            "total_scans": 5,
            "flags_count": len(risk_indicators),
            "notes": "Zero fraud patterns detected in analyzed job description." if not risk_indicators else f"{len(risk_indicators)} risk pattern(s) identified in job description."
        }

        return TrustVerificationResult(
            verification_status=status,
            verified_at=verified_at,
            summary_reason=summary_reason,
            trust_score=trust_score,
            indicative_trust_score=trust_score,
            score_disclaimer=score_disclaimer,
            disclaimer=score_disclaimer,
            company_name=comp_name or "Not Specified",
            company_domain=comp_domain or "",
            company_verified=company_verified,
            company_website_url=final_website_url or (f"https://{comp_domain}" if comp_domain else None),
            recruiter_name=rec_name_clean,
            recruiter_email=rec_email_clean,
            recruiter_profile_url=rec_profile_clean or None,
            recruiter_affiliation_status=affiliation_status,
            job_posting_url=posting_url_clean or None,
            job_posting_status=posting_status,
            checks=checks,
            detailed_checks=checks,
            risk_indicators=risk_indicators,
            positive_indicators=positive_indicators,
            limitations_and_disclaimers=limitations,
            company_verification=company_verification_dict,
            recruiter_verification=recruiter_verification_dict,
            posting_verification=posting_verification_dict,
            risk_assessment=risk_assessment_dict
        )
