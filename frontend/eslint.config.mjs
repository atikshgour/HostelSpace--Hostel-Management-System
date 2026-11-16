/* Owner: Anvi Srinivas | US-17,US-01 | Dev sprint 1 | SRS sprint 1 | Reviewer: Arin Singh (pending) */
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
export default defineConfig([
  ...nextVitals,
  globalIgnores([".next/**"]),
  {
    rules: {
      "react-hooks/set-state-in-effect": "off",
      "react-hooks/exhaustive-deps": "warn",
    },
  },
]);
