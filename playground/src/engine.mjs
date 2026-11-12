// Kattour Guardian Playground — deterministic, offline planning engine.
// No model or vendor API calls are made, and metrics are not billed token counts.
export const PROJECT_TYPES = ['Web application','Website','Mobile application','API / backend','Desktop application'];
export const STACKS = ['Next.js + TypeScript','React + Vite','Vue + Nuxt','SvelteKit','Flutter','React Native','Laravel + PHP','Django + Python','FastAPI + Python','Node.js + Fastify','HTML + CSS + JavaScript'];
export const PLATFORMS = ['Web','Progressive Web App','iOS','Android','iOS + Android','Desktop','Cross-platform'];
export const PRESETS = [
  { label:'SaaS dashboard', type:'Web application', stack:'Next.js + TypeScript', platform:'Web', goal:'Build a multi-tenant SaaS analytics dashboard with secure sign-in, role-based permissions, clear KPIs, and accessible responsive charts.' },
  { label:'Food delivery', type:'Web application', stack:'Next.js + TypeScript', platform:'Progressive Web App', goal:'Build a responsive food delivery ordering experience with restaurant discovery, cart, checkout, order tracking, and clear failure states.' },
  { label:'Booking portal', type:'Website', stack:'Vue + Nuxt', platform:'Web', goal:'Create a modern booking portal with service search, available slots, confirmation, mobile-first navigation, and accessible forms.' },
  { label:'Mobile commerce', type:'Mobile application', stack:'Flutter', platform:'iOS + Android', goal:'Build a mobile shopping app with product browsing, saved favorites, a secure checkout flow, and polished loading and empty states.' },
];
const SECRET = /\b(api[_ -]?key|access[_ -]?token|client[_ -]?secret|password|private[_ -]?key)\s*[:=]\s*["']?[^\s"']{5,}/gi;
const KEY_BLOCK = /-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/i;
const STANDARDS = 'KG-C1: Implement mobile-first responsive layout, semantic controls, accessible labels and keyboard focus, useful loading/empty/error states, typed input validation, server-side authorization, safe secret handling, and automated tests. Run verification before claiming completion.';
export const SHARED_BLOCK_ID = 'KG-C1';
export function redact(text='') { return String(text).replace(SECRET, '$1=[REDACTED]').replace(/-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/g,'[REDACTED PRIVATE KEY]'); }
export function containsSecrets(text='') { SECRET.lastIndex=0; return SECRET.test(String(text)) || KEY_BLOCK.test(String(text)); }
export function normalizedInput(data={}) {
  return {
    type: PROJECT_TYPES.includes(data.type) ? data.type : PROJECT_TYPES[0],
    stack: STACKS.includes(data.stack) ? data.stack : STACKS[0],
    platform: PLATFORMS.includes(data.platform) ? data.platform : PLATFORMS[0],
    goal: String(data.goal || '').replace(/\r/g,'').trim().slice(0,4800),
    constraints: String(data.constraints || '').replace(/\r/g,'').trim().slice(0,1400)
  };
}
export function estimateTokens(text) { return Math.max(0, Math.ceil(String(text).length/4)); }
export function percentReduction(before, after) { return before ? Math.round((1 - after / before) * 100) : 0; }
const safeTitle = str => str.replace(/[^a-zA-Z0-9 -]/g,'').replace(/\s+/g,' ').trim().slice(0,40);
function focusOf(text) {
  const s=text.toLowerCase();
  for(const [pattern,focus] of [
    [/checkout|cart|payment|purchase|order/, 'checkout'], [/booking|appointment|reservation|calendar/, 'booking'],
    [/dashboard|analytics|kpi|report|insight/, 'dashboard'], [/auth|login|sign.in|account|identity/, 'accounts'],
    [/shop|store|catalog|product|commerce/, 'catalog'], [/chat|message|support|inbox/, 'messaging'],
    [/delivery|driver|dispatch|track/, 'delivery'], [/portfolio|landing|marketing/, 'landing']
  ]) if(pattern.test(s))return focus;
  return 'core';
}
function filesFor(d, focus) {
  const f=focus.replace(/[^a-z]/g,'');
  let paths;
  if(d.stack.startsWith('Next.js')) paths=[['app/layout.tsx','Global layout and metadata'],['app/page.tsx','Main screen and entry flow'],[`app/${f}/page.tsx`,'Feature page'],[`app/api/${f}/route.ts`,'Validated API boundary'],[`components/${f}/feature-panel.tsx`,'Accessible reusable UI'],['lib/auth.ts','Session and permission enforcement'],['lib/validation.ts','Input schemas'],[`tests/${f}.test.ts`,'Feature and edge-case tests']];
  else if(d.stack.startsWith('React +'))paths=[['src/main.tsx','App bootstrap'],['src/App.tsx','Routing and shell'],[`src/features/${f}/index.tsx`,'Main feature screen'],[`src/features/${f}/service.ts`,'Typed data boundary'],['src/components/ui/','Reusable accessible components'],['src/lib/validation.ts','Input validation'],[`tests/${f}.test.tsx`,'Behavioral tests']];
  else if(d.stack.startsWith('Vue'))paths=[['app.vue','App shell'],[`pages/${f}.vue`,'Feature page'],[`components/${f}/FeaturePanel.vue`,'Reusable view'],[`composables/use${capitalize(f)}.ts`,'Feature state'],['server/api/','Server-side API boundaries'],[`tests/${f}.test.ts`,'Feature tests']];
  else if(d.stack==='SvelteKit')paths=[['src/app.html','Application document'],[`src/routes/${f}/+page.svelte`,'Feature page'],[`src/routes/api/${f}/+server.ts`,'Validated server endpoint'],[`src/lib/${f}/service.ts`,'Data and state layer'],['src/lib/components/','Accessible shared components'],[`tests/${f}.test.ts`,'Feature tests']];
  else if(d.stack==='Flutter')paths=[['lib/main.dart','App initialization'],[`lib/features/${f}/presentation/screen.dart`,'Primary feature screen'],[`lib/features/${f}/domain/model.dart`,'Domain models'],[`lib/features/${f}/data/repository.dart`,'Data repository'],['lib/shared/widgets/','Reusable accessible widgets'],[`test/${f}_test.dart`,'Widget and logic tests']];
  else if(d.stack==='React Native')paths=[['src/App.tsx','App root'],[`src/features/${f}/screen.tsx`,'Feature screen'],[`src/features/${f}/api.ts`,'Typed API client'],['src/navigation/index.tsx','Navigation'],['src/components/','Shared UI'],[`__tests__/${f}.test.tsx`,'UI tests']];
  else if(d.stack.startsWith('Laravel'))paths=[['routes/web.php','Application routes'],['routes/api.php','API routes'],[`app/Http/Controllers/${capitalize(f)}Controller.php`,'Feature controller'],[`app/Http/Requests/${capitalize(f)}Request.php`,'Validation'],['app/Policies/','Authorization'],[`resources/views/${f}/index.blade.php`,'Accessible interface'],[`tests/Feature/${capitalize(f)}Test.php`,'Feature tests']];
  else if(d.stack.startsWith('Django'))paths=[['config/settings.py','Security-conscious settings'],[`apps/${f}/views.py`,'Feature handlers'],[`apps/${f}/models.py`,'Domain data'],[`apps/${f}/urls.py`,'Routes'],[`apps/${f}/templates/`,'Accessible views'],[`apps/${f}/tests.py`,'Feature tests']];
  else if(d.stack.startsWith('FastAPI'))paths=[['app/main.py','Service entry'],[`app/api/${f}.py`,'Validated endpoint'],[`app/schemas/${f}.py`,'Request and response models'],[`app/services/${f}.py`,'Business logic'],['app/security.py','Authorization boundaries'],[`tests/test_${f}.py`,'API tests']];
  else if(d.stack.startsWith('Node.js'))paths=[['src/server.ts','Server bootstrap'],[`src/routes/${f}.ts`,'Validated endpoints'],[`src/services/${f}.ts`,'Domain logic'],['src/lib/auth.ts','Authentication and authorization'],['src/lib/schema.ts','Input schemas'],[`tests/${f}.test.ts`,'API tests']];
  else paths=[['index.html','Semantic page layout'],['styles/main.css','Responsive design system'],['scripts/app.js','Interactions and state'],['scripts/validation.js','Client input checks'],['assets/','Optimized visual assets'],['tests/ui.test.js','UI and behavior tests']];
  return paths.map(([path,purpose])=>({path,purpose}));
}
const capitalize = s => s.charAt(0).toUpperCase()+s.slice(1);
export function isCompatible(d) {
  if(d.type==='Mobile application' && ['Web','Desktop'].includes(d.platform)) return false;
  if(d.type==='Desktop application' && ['iOS','Android','iOS + Android'].includes(d.platform)) return false;
  if(d.type==='API / backend' && ['iOS','Android','iOS + Android','Desktop'].includes(d.platform)) return false;
  if(d.stack==='Flutter' && d.platform==='Web') return true;
  if(['React Native'].includes(d.stack) && d.type==='API / backend') return false;
  return true;
}
export function generateProject(raw) {
  const d=normalizedInput(raw), focus=focusOf(d.goal), cleanGoal=redact(d.goal), cleanConstraints=redact(d.constraints);
  const featureLabel=focus==='core' ? 'primary workflow' : focus+' workflow';
  const files=filesFor(d, focus);
  const phases=[
    {title:'01 · Scope & architecture',description:`Map the ${featureLabel}, user roles, data boundaries and acceptance criteria. Pick the smallest maintainable ${d.stack} structure.`},
    {title:'02 · Implement core experience',description:`Build the main ${d.type.toLowerCase()} journey, reusable components, real interaction states, input validation and authorization boundaries.`},
    {title:'03 · Verify UI & security',description:'Test keyboard and mobile flows, edge cases, role permissions and failure recovery. Triage static findings rather than assuming they are vulnerabilities.'},
    {title:'04 · Prepare release',description:'Run build/tests, review performance and accessibility, document known gaps, and define rollback and observability.'}
  ];
  const tasks=[
    ['Define user roles, acceptance criteria and main success flow','P0','Discovery'],
    [`Create the ${d.stack} feature skeleton and routes`,'P0','Build'],
    [`Implement the ${featureLabel} with loading, empty and error states`,'P0','Build'],
    ['Validate inputs and enforce permissions at trusted boundaries','P0','Security'],
    ['Establish responsive layout, semantic controls and keyboard navigation','P1','UX'],
    ['Add unit and integration tests for success and failure paths','P1','Verification'],
    ['Review secrets, dependencies and data exposure risks','P1','Security'],
    ['Check mobile layout, accessibility and performance evidence','P1','Verification'],
    ['Document release, monitoring, rollback and unresolved risks','P2','Release'],
  ].map(([title,priority,phase],id)=>({id,title,priority,phase}));
  const ux=[
    {title:'Clear primary action',text:`Make the ${featureLabel} immediately discoverable, with one obvious next step and clear page hierarchy.`},
    {title:'Responsive by default',text:'Support narrow mobile screens, touch-friendly spacing, readable text and layouts without horizontal overflow.'},
    {title:'States that explain themselves',text:'Design skeleton/loading, empty, validation, permission, error and success states with useful recovery paths.'},
    {title:'Inclusive interactions',text:'Use semantic labels, visible focus, keyboard paths, sufficient contrast and accessible feedback.'},
    {title:'Trust & transparency',text:'Explain sensitive actions, confirmation, privacy choices and irreversible changes before users commit.'},
    {title:'Performance budget',text:'Avoid redundant fetches and oversized assets; measure key flows before claiming performance improvements.'},
  ];
  const requirements=[`Project: ${d.type} / ${d.stack} / ${d.platform}`,`Goal: ${cleanGoal}`,cleanConstraints?`Constraints: ${cleanConstraints}`:'',`Core focus: ${featureLabel}`].filter(Boolean);
  const fullPrompt=[
    'ROLE: Senior product engineer, UI/UX specialist, and defensive security reviewer.',
    ...requirements,'', 'IMPLEMENTATION PLAN:',
    ...phases.map((p,i)=>`${i+1}. ${p.title.replace(/^\d+ · /,'')}: ${p.description}`),'',
    'SUGGESTED FILES:',...files.map(f=>`- ${f.path} — ${f.purpose}`),'',
    'TASK BACKLOG:',...tasks.map((t,i)=>`${i+1}. [${t.priority}] ${t.title}`),'',
    'UI/UX CRITERIA:',...ux.map(x=>`- ${x.title}: ${x.text}`),'',
    'VERIFICATION: Test inputs and authorization, run relevant unit/integration tests, check accessibility and mobile states, report measured evidence, blockers and untested areas.',
    'SECURITY: Do not expose secrets, never claim 100% security; require server-side authorization and safe failure behavior.',
    'RESPONSE FORMAT: Provide implementation steps, changed files, test evidence, remaining risks. Do not invent results.'
  ].join('\n');
  const shortPrompt=[
    `Act as a senior ${d.stack} engineer with strong UX and application security practice.`,
    ...requirements,
    `Plan: ${phases.map(p=>p.title.replace(/^\d+ · /,'')).join(' → ')}.`,
    `Deliver: ${tasks.slice(0,6).map(t=>t.title.replace(/[.]$/,'')).join('; ')}.`,
    `Starting files: ${files.slice(0,6).map(f=>f.path).join(', ')}.`,
    STANDARDS,
    'Output concise steps, file changes, verification evidence and unresolved risks. No invented test results.'
  ].join('\n');
  return {input:d,focus,files,phases,tasks,ux,fullPrompt,shortPrompt,sharedStandards:STANDARDS,createdAt:new Date().toISOString()};
}
export function optimizedPrompt(project, {reuse=false, sharedSent=false}={}) {
  if(!project)return '';
  if(!reuse || !sharedSent)return project.shortPrompt;
  return project.shortPrompt.replace(project.sharedStandards,'Reuse the previously supplied KG-C1 standards in this same AI conversation (do not omit them in a new chat).');
}
export function buildQA(project, prompt, {reuse=false,sharedSent=false}={}) {
  if(!project)return [{name:'Generate an output first',status:'fail',detail:'Enter a project goal and generate a workspace.'}];
  const d=project.input;
  const tests=[
    {name:'Specific goal', pass:d.goal.length>=18,detail:'Goal has enough detail to guide implementation.'},
    {name:'Supported configuration', pass:isCompatible(d),detail:'Project type and target platform are logically compatible.'},
    {name:'Secrets excluded', pass:!containsSecrets(d.goal+'\n'+d.constraints),detail:'No credential-like value detected in input. Automated checks are not exhaustive.'},
    {name:'Actionable implementation plan',pass:project.phases.length>=4 && project.tasks.length>=7,detail:'Includes staged delivery and prioritized backlog.'},
    {name:'File architecture',pass:project.files.length>=5,detail:'Includes a concrete starting folder/file map.'},
    {name:'UX and accessible interactions',pass:project.ux.length>=4 && (/keyboard|accessible/i.test(prompt) || (reuse && sharedSent)),detail:'Covers responsive, keyboard and interaction states.'},
    {name:'Security and test coverage',pass:/authorization|permissions/i.test(prompt)&&/test/i.test(prompt),detail:'Retains authorization and verification responsibilities.'},
    {name:'Context reuse safety',pass:!reuse || sharedSent,detail:'References are used only after shared standards have been sent to the same AI conversation.'},
  ];
  return tests.map(t=>({...t,status:t.pass?'pass':'fail'}));
}
export function exportMarkdown(project,prompt,tests) {
  const d=project.input;
  return [`# Kattour Guardian · ${d.type}`,``, `**Stack:** ${d.stack}  `,`**Platform:** ${d.platform}  `,`**Goal:** ${redact(d.goal)}`, d.constraints?`**Constraints:** ${redact(d.constraints)}`:'',``,`## Execution plan`,...project.phases.map(x=>`- **${x.title}** — ${x.description}`),``,`## Proposed file tree`, '```text', ...project.files.map(x=>x.path),'```','',`## Tasks`,...project.tasks.map(t=>`- [ ] **${t.priority}** ${t.title}`),'',`## UI/UX recommendations`,...project.ux.map(x=>`- **${x.title}:** ${x.text}`),'',`## Quality gate`,...tests.map(t=>`- ${t.status==='pass'?'PASS':'FAIL'} · ${t.name}`),'',`## Optimized prompt`,'```text',prompt,'```','',`*Generated offline from deterministic templates. Inspect and adapt before production use.*`].filter(x=>x!==undefined).join('\n');
}
export function exportJSON(project,prompt,tests) {
  return JSON.stringify({schema:'kattour-guardian-playground/1.0',input:{...project.input,goal:redact(project.input.goal),constraints:redact(project.input.constraints)},focus:project.focus,phases:project.phases,files:project.files,tasks:project.tasks,ux:project.ux,optimized_prompt:prompt,quality_checks:tests.map(({name,status,detail})=>({name,status,detail})),token_estimates:{baseline:estimateTokens(project.fullPrompt),optimized:estimateTokens(prompt),method:'characters / 4; not a model tokenizer'},created_at:project.createdAt},null,2);
}