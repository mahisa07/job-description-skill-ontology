from typing import List, Dict, Any
from backend.models.schemas import OntologyGraph, OntologyNode, OntologyEdge, SkillMention
from backend.services.skill_normalizer import SkillNormalizerService

class OntologyService:
    @staticmethod
    def build_ontology(job_role: str, skills: List[SkillMention]) -> OntologyGraph:
        nodes: List[OntologyNode] = []
        edges: List[OntologyEdge] = []
        seen_nodes = set()

        # 1. Job Role Node (Root)
        role_id = f"role_{job_role.lower().replace(' ', '_')}"
        nodes.append(OntologyNode(
            id=role_id,
            label=job_role,
            type="role"
        ))
        seen_nodes.add(role_id)

        # Group skills by category
        categories: Dict[str, List[SkillMention]] = {}
        for skill in skills:
            categories.setdefault(skill.category, []).append(skill)

        # 2. Category Nodes & Category Edges
        for cat_name, cat_skills in categories.items():
            cat_id = f"cat_{cat_name.lower().replace(' ', '_')}"
            if cat_id not in seen_nodes:
                nodes.append(OntologyNode(
                    id=cat_id,
                    label=cat_name,
                    type="category"
                ))
                seen_nodes.add(cat_id)

            # Job Role -> Category relation
            edges.append(OntologyEdge(
                source=role_id,
                target=cat_id,
                relation="has_category"
            ))

            # 3. Skill Nodes & Edges
            for skill in cat_skills:
                skill_id = f"skill_{skill.canonical_name.lower().replace(' ', '_')}"
                if skill_id not in seen_nodes:
                    nodes.append(OntologyNode(
                        id=skill_id,
                        label=skill.canonical_name,
                        type="skill",
                        category=skill.category,
                        requirement_level=skill.requirement_level,
                        importance=skill.importance
                    ))
                    seen_nodes.add(skill_id)

                # Job Role -> requires -> Skill
                edges.append(OntologyEdge(
                    source=role_id,
                    target=skill_id,
                    relation="requires"
                ))

                # Skill -> belongs_to -> Category
                edges.append(OntologyEdge(
                    source=skill_id,
                    target=cat_id,
                    relation="belongs_to"
                ))

                # 4. Related Skills Nodes & Edges
                related_list = SkillNormalizerService.get_related_skills(skill.canonical_name)
                for rel_name in related_list[:3]:  # max top 3 related
                    rel_id = f"related_{rel_name.lower().replace(' ', '_')}"
                    if rel_id not in seen_nodes and rel_id != skill_id:
                        rel_cat = SkillNormalizerService.CATEGORY_MAP.get(rel_name, "Tools & Other")
                        nodes.append(OntologyNode(
                            id=rel_id,
                            label=rel_name,
                            type="related_skill",
                            category=rel_cat,
                            requirement_level="OPTIONAL",
                            importance="Low"
                        ))
                        seen_nodes.add(rel_id)

                        # Skill -> is_related_to -> Related Skill
                        edges.append(OntologyEdge(
                            source=skill_id,
                            target=rel_id,
                            relation="is_related_to"
                        ))

        return OntologyGraph(nodes=nodes, edges=edges)

    @staticmethod
    def generate_academic_comparison(job_role: str, skills: List[SkillMention]) -> Dict[str, Any]:
        """
        Generates structured contrast demonstrating why Ontology is superior to simple keyword extraction.
        """
        raw_keywords = [s.original_mention for s in skills]
        normalized_skills = [s.canonical_name for s in skills]

        hierarchy = {}
        for s in skills:
            hierarchy.setdefault(s.category, []).append(s.canonical_name)

        return {
            "academic_title": "Comparative Analysis: Traditional Keyword Extraction vs. Ontology-Based Representation",
            "traditional_extraction": {
                "format": "Flat Unstructured Keyword Array",
                "extracted_keywords": raw_keywords,
                "limitations": [
                    "No understanding of skill canonical normalization (treats ML and Machine Learning as separate terms)",
                    "No contextual requirement tagging (cannot distinguish between Required vs Preferred vs Optional)",
                    "No semantic categorizations (treats Python, SQL, and Communication as flat list)",
                    "No entity relationship mapping (cannot trace which role or category requires which skill)"
                ]
            },
            "ontology_representation": {
                "format": "Interconnected Semantic Knowledge Graph (OWL/RDF Taxonomy Structure)",
                "job_role": job_role,
                "categorized_hierarchy": hierarchy,
                "ontology_advantages": [
                    "Structured knowledge hierarchy (Job Role → Skill Category → Canonical Skill → Related Skill)",
                    "Canonical normalization mapping (raw aliases mapped to standard skill taxonomy)",
                    "Contextual requirement level classification (REQUIRED, PREFERRED, OPTIONAL)",
                    "Explicit semantic relationships (requires, belongs_to, is_related_to)",
                    "Foundation for explainable resume matching and skill-gap proximity analysis"
                ]
            }
        }
