import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import 'vitest/config'
// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom'
  },
})
