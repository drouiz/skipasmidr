// Patches the generated Backstage app to remove the scaffolder plugin,
// which depends on isolated-vm (fails to compile in Docker environments).
// Catalog, search and TechDocs continue to work without the scaffolder.

const fs = require('fs');

// ── 1. Remove scaffolder packages from backend/package.json ─────────────────
const pkgPath = 'packages/backend/package.json';
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
const deps = pkg.dependencies || {};
const removed = Object.keys(deps).filter(k => k.includes('scaffolder'));
removed.forEach(k => delete deps[k]);
if (removed.length) {
  fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2));
  console.log('Removed from package.json:', removed.join(', '));
}

// ── 2. Remove scaffolder imports from backend/src/index.ts ──────────────────
const indexPath = 'packages/backend/src/index.ts';
let content = fs.readFileSync(indexPath, 'utf8');

// Single-line: backend.add(import('@backstage/plugin-scaffolder-...'));
content = content.replace(/\nbackend\.add\(import\('[^']*scaffolder[^']*'\)\);/g, '');

// Multi-line — closing ); may be at column 0 (no indent), so use \s* not \s+:
//   backend.add(
//     import('@backstage/plugin-scaffolder-...'),
//   );          ← or );  at column 0
content = content.replace(/\nbackend\.add\(\n\s*import\('[^']*scaffolder[^']*'\),\n\s*\);/g, '');

// Remove any leftover empty backend.add() calls (artifact from the above)
content = content.replace(/\nbackend\.add\(\s*\);/g, '');

// Remove orphan scaffolder comment lines
content = content.replace(/\n\/\/ scaffolder plugin\n/g, '\n');

fs.writeFileSync(indexPath, content);
console.log('Cleaned scaffolder imports from index.ts');
