import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/upload': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/chat': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/clear-conversation': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/status': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
