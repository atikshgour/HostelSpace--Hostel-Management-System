// Owner: Atiksh | US-20 | Sprint 1
import nextJest from 'next/jest.js';
const createConfig = nextJest({ dir: './' });
export default createConfig({ testEnvironment: 'jsdom', roots: ['<rootDir>/app'], setupFilesAfterEnv: ['<rootDir>/jest.setup.js'], collectCoverageFrom: ['app/page.js', 'app/health/route.js'], coverageThreshold: { global: { lines: 100, statements: 100, functions: 100 } } });
