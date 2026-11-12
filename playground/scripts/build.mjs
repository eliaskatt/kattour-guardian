/**
 * Dependency-free packaging: keep the offline standalone index.html in sync
 * with the independently testable modular sources in src/.
 */
import {readFile, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {dirname, join, resolve} from 'node:path';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const read=(p)=>readFile(join(root,p),'utf8');
let [html,css,engine,app]=await Promise.all([read('src/index.html'),read('src/styles.css'),read('src/engine.mjs'),read('src/app.js')]);
if(!html.includes('<link rel="stylesheet" href="./styles.css">') || !html.includes('<script type="module" src="./app.js"></script>'))throw new Error('Unsupported HTML entrypoint');
const importLine=/^import\s*\{[^}]+\}\s*from\s*['"]\.\/engine\.mjs['"];?\s*\n/m;
if(!importLine.test(app))throw new Error('Expected engine import not found');
app=app.replace(importLine,'');
engine=engine.replace(/^export (const|function) /gm,'$1 ');
// Disallow premature inline script terminators from future source changes.
const safeScript=(value)=>value.replaceAll('</script','<\\/script');
html=html.replace('<link rel="stylesheet" href="./styles.css">',`<style>\n${css}\n</style>`);
html=html.replace('<script type="module" src="./app.js"></script>',`<script>\n${safeScript(engine)}\n${safeScript(app)}\n</script>`);
const dest=join(root,'index.html');
if(process.argv.includes('--check')){
 const existing=await readFile(dest,'utf8');
 if(existing!==html){console.error('Standalone playground/index.html is stale; run node playground/scripts/build.mjs');process.exit(1);}
 console.log('PASS: standalone HTML matches modular source');
}else{await writeFile(dest,html,'utf8'); console.log('Built offline playground/index.html');}
