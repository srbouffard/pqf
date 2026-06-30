/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  base: './',
  // Serve ../public/ as static assets during dev so /portfolio.json resolves
  publicDir: path.resolve(__dirname, '../public'),
  resolve: {
    alias: {
      'vanilla-framework': path.resolve(__dirname, 'node_modules/vanilla-framework'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test-setup.ts'],
  },
})
