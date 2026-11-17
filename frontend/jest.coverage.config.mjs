// Team test review | US-18/21/23 | Include every implemented source module.
import base from './jest.config.mjs';
const coverageConfig = async () => ({
  ...await base(),
});
export default coverageConfig;
