import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiUrl = env.VITE_API_URL || ''

  return {
    plugins: [
      react(),
      {
        name: 'html-transform',
        transformIndexHtml(html) {
          if (apiUrl) {
            return html.replace(
              /<meta name="api-base-url" content="[^"]*"/,
              `<meta name="api-base-url" content="${apiUrl}"`
            )
          }
          return html
        }
      }
    ],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: apiUrl || 'http://localhost:8000',
          changeOrigin: true
        }
      }
    }
  }
})
