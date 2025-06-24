import {defineConfig, loadEnv} from 'vite'
import react from '@vitejs/plugin-react'
import 'vitest/config'
// https://vite.dev/config/
export default defineConfig(({mode}) => {

    const env = loadEnv(mode, process.cwd())
    return {
        plugins: [react()],
        build: {
            sourcemap: false,
        },
        test: {
            environment: 'jsdom',
            globals: true,
            setupFiles: '/src/tests/setup_tests.ts',
            coverage: {
                include: ['src/**/*.{ts,tsx,js,jsx}']
            }
        },
        server: {
            host: env.VITE_CLIENT_HOST || 'localhost',
            port: parseInt(env.VITE_CLIENT_PORT) || 5173
        }
    }
})
