// Owner: Atiksh Gour | US-20: expose implemented src/app routes during team merges.
import { readdirSync, readFileSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';
const marker = '// Generated route adapter: scripts/sync-app-routes.mjs';
for (const relative of readdirSync('src/app', {recursive: true})) {
  const path = relative.replaceAll('\\', '/');
  if (!/(^|\/)(page|layout|loading|error|not-found|route)\.[jt]sx?$/.test(path)) continue;
  const source = readFileSync(`src/app/${path}`, 'utf8');
  if (source.includes('STATUS: Instruction-filled starter; application behavior NOT IMPLEMENTED.')) continue;
  const target = `app/${path}`;
  if (existsSync(target)) {
    const previous = readFileSync(target, 'utf8');
    if (!previous.startsWith(marker) && !previous.startsWith('export { default } from "@/app/')) continue;
  }
  mkdirSync(dirname(target), {recursive: true});
  const exports = path.endsWith('route.js') ? 'export *' : 'export { default }';
  writeFileSync(target, `${marker}\n${exports} from "@/app/${path}";\n`);
}
