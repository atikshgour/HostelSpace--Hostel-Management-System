// Owner: Atiksh | US-20 | Sprint 1
import { defineConfig, globalIgnores } from 'eslint/config';
import nextVitals from 'eslint-config-next/core-web-vitals';
export default defineConfig([...nextVitals, globalIgnores(['src/**', '.next/**', 'coverage/**']), { files: ['**/*.test.*', 'jest.setup.js'], languageOptions: { globals: { test: 'readonly', expect: 'readonly' } } }]);
