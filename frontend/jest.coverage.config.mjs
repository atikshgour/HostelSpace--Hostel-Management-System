// Team test review | US-18/21/23 | Include every implemented source module.
import base from './jest.config.mjs';
import {readdirSync, readFileSync} from 'node:fs';

const coverageConfig = async () => ({
  ...await base(),
  collectCoverageFrom: readdirSync('src', {recursive:true})
    .map(name => `src/${name}`.replaceAll('\\', '/'))
    .filter(name => /\.[jt]sx?$/.test(name) && !/\.test\./.test(name))
    .filter(name => !readFileSync(name, 'utf8').includes('STATUS: Instruction-filled starter; application behavior NOT IMPLEMENTED.')),
  coverageReporters: ['text', 'json', 'json-summary', 'lcovonly', 'html'],
});
export default coverageConfig;
