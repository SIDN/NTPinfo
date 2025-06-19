import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import 'vitest/config'
// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: '/src/tests/setup_tests.ts',
    coverage: {
      include: ['src/**/*.{ts,tsx,js,jsx}']
    }
  },
})
