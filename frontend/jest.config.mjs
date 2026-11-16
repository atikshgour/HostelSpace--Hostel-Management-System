// Owner: Atiksh Gour | US-20 | Sprint 1
import nextJest from 'next/jest.js';
import { readdirSync, readFileSync } from 'node:fs';
const createConfig = nextJest({ dir: './' });
const testFiles = ['src'].flatMap(root => readdirSync(root, { recursive: true })
  .map(name => `${root}/${name}`.replaceAll('\\', '/'))
  .filter(name => /\.test\.[jt]sx?$/.test(name))
  // Starter task comments contain no executable tests. Replacements join CI automatically.
  .filter(name => !readFileSync(name, 'utf8').includes('STATUS: Instruction-filled starter; application behavior NOT IMPLEMENTED.'))
  .map(name => `<rootDir>/${name}`));
export default createConfig({
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: { '^@/(.*)$': '<rootDir>/src/$1' },
  modulePathIgnorePatterns: ['<rootDir>/.next/'],
  testMatch: testFiles,
  coverageThreshold: {
    './src/app/health/route.js': { lines: 100, statements: 100, functions: 100 },
  },
});
