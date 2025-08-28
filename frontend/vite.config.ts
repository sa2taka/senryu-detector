/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  build: {
    outDir: '../docs',
  },
  define: {
    __API_BASE_URL__: JSON.stringify(
      !mode || mode === 'development'
        ? 'http://localhost:8000'
        : 'https://your-api-domain.com'
    ),
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
}))
