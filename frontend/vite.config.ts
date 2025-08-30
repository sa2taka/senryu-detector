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
        ? 'http://localhost:8080'
        : 'https://senryu-detector-111226594682.asia-northeast1.run.app'
    ),
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
}))
