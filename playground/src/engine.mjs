// Kattour Guardian Playground — deterministic, offline planning engine.
// No model or vendor API calls are made, and metrics are not billed token counts.
export const PROJECT_TYPES = ['Web application','Website','Mobile application','API / backend','Desktop application'];
export const STACKS = ['Next.js + TypeScript','React + Vite','Vue + Nuxt','SvelteKit','Flutter','React Native','Laravel + PHP','Django + Python','FastAPI + Python','Node.js + Fastify','HTML + CSS + JavaScript'];
export const PLATFORMS = ['Web','Progressive Web App','iOS','Android','iOS + Android','Desktop','Cross-platform'];
export const WORK_MODES = ['Build feature','Fix a bug','Security review','UI/UX improvement','Performance review'];
export const TARGET_AGENTS = ['Any coding agent','OpenAI Codex','Claude Code','Cursor','GitHub Copilot','Gemini CLI'];
export const DETAIL_LEVELS = ['Lean','Balanced','Thorough'];
const AGENT_GUIDANCE = {
  'Any coding agent':'Use repository conventions. Work in verifiable increments and distinguish completed work from recommendations.',
  'OpenAI Codex':'Inspect project files before edits; make minimal reviewable patches and report tests actually executed.',
  'Claude Code':'Explore relevant code paths before proposing changes. Track assumptions and summarize evidence and open issues.',
  'Cursor':'Prefer precise paths and symbols in the active workspace. Avoid unrelated refactoring and validate changed flows.',
  'GitHub Copilot':'Follow repository instructions and coding patterns. Provide small diffs with tests and clear acceptance criteria.',
  'Gemini CLI':'Use targeted workspace discovery and concise file references. Explain tool results without inventing execution.'
};
export const PRESETS = [
  { label:'SaaS dashboard', type:'Web application', stack:'Next.js + TypeScript', platform:'Web', goal:'Build a multi-tenant SaaS analytics dashboard with secure sign-in, role-based permissions, clear KPIs, and accessible responsive charts.' },
  { label:'Food delivery', type:'Web application', stack:'Next.js + TypeScript', platform:'Progressive Web App', goal:'Build a responsive food delivery ordering experience with restaurant discovery, cart, checkout, order tracking, and clear failure states.' },
  { label:'Booking portal', type:'Website', stack:'Vue + Nuxt', platform:'Web', goal:'Create a modern booking portal with service search, available slots, confirmation, mobile-first navigation, and accessible forms.' },
  { label:'Mobile commerce', type:'Mobile application', stack:'Flutter', platform:'iOS + Android', goal:'Build a mobile shopping app with product browsing, saved favorites, a secure checkout flow, and polished loading and empty states.' },
  { label:'Bug triage',mode:'Fix a bug',type:'Web application',stack:'React + Vite',platform:'Web',goal:'Fix the checkout form losing customer input after a failed payment request, while preserving validation and keyboard accessibility.' },
  { label:'Security readiness',mode:'Security review',type:'Web application',stack:'Next.js + TypeScript',platform:'Web',goal:'Review a multi-tenant account dashboard for access control, secret handling, input validation and safe failure behavior. Perform only authorized static checks.' },
  { label:'UI/UX refresh',mode:'UI/UX improvement',type:'Website',stack:'Vue + Nuxt',platform:'Web',goal:'Improve mobile booking completion by simplifying the search form, making actions prominent and adding accessible loading and error states.' },
  { label:'Performance triage',mode:'Performance review',type:'Web application',stack:'Next.js + TypeScript',platform:'Web',goal:'Reduce slow mobile dashboard loading by measuring image sizes, render delays and duplicate requests on a repeatable test device.' },
];
const SECRET = /\b(api[_ -]?key|access[_ -]?token|client[_ -]?secret|password|private[_ -]?key)\s*[:=]\s*["']?[^\s"']{5,}/gi;
const KEY_BLOCK = /-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/i;
const EXPOSED_TOKEN = /\b(?:ghp_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}|sk_(?:live|test)_[A-Za-z0-9]{16,}|AKIA[A-Z0-9]{16})\b/g;
const STANDARDS = 'KG-C1: Preserve mobile-first responsive layout, semantic controls, accessible labels and keyboard focus, useful loading/empty/error states, typed input validation, server-side authorization, safe secret handling, and automated tests. Run verification before claiming completion.';
export const SHARED_BLOCK_ID = 'KG-C1';
export function redact(text='') { return String(text).replace(SECRET, '$1=[REDACTED]').replace(EXPOSED_TOKEN,'[REDACTED TOKEN]').replace(/-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/g,'[REDACTED PRIVATE KEY]'); }
export function containsSecrets(text='') { SECRET.lastIndex=0; EXPOSED_TOKEN.lastIndex=0; return SECRET.test(String(text)) || EXPOSED_TOKEN.test(String(text)) || KEY_BLOCK.test(String(text)); }
export function normalizedInput(data={}) {
  return {
    type: PROJECT_TYPES.includes(data.type) ? data.type : PROJECT_TYPES[0],
    mode: WORK_MODES.includes(data.mode) ? data.mode : WORK_MODES[0],
    agent: TARGET_AGENTS.includes(data.agent) ? data.agent : TARGET_AGENTS[0],
    detail: DETAIL_LEVELS.includes(data.detail) ? data.detail : DETAIL_LEVELS[1],
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
  let phases=[
    {title:'01 · Scope & architecture',description:`Map the ${featureLabel}, user roles, data boundaries and acceptance criteria. Pick the smallest maintainable ${d.stack} structure.`},
    {title:'02 · Implement core experience',description:`Build the main ${d.type.toLowerCase()} journey, reusable components, real interaction states, input validation and authorization boundaries.`},
    {title:'03 · Verify UI & security',description:'Test keyboard and mobile flows, edge cases, role permissions and failure recovery. Triage static findings rather than assuming they are vulnerabilities.'},
    {title:'04 · Prepare release',description:'Run build/tests, review performance and accessibility, document known gaps, and define rollback and observability.'}
  ];
  let tasks=[
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
  // Mode-specific delivery plans replace generic advice rather than pretending to analyze actual source code.
  if (d.mode === 'Fix a bug') {
    phases = [
      {title:'01 · Reproduce and bound',description:'Capture exact steps, expected versus actual behavior, environment, error text and the affected user journey without exposing secrets.'},
      {title:'02 · Trace the root cause',description:`Inspect the relevant ${d.stack} call path and hypotheses; collect evidence before choosing a fix.`},
      {title:'03 · Apply the smallest safe fix',description:'Patch the underlying cause, preserve existing architecture and avoid speculative rewrites or unrelated changes.'},
      {title:'04 · Prove the regression is fixed',description:'Add a failing-then-passing regression test, recheck boundary cases, and report remaining risks and untested paths.'}
    ];
    tasks = [
      ['Write reproduction steps and expected vs actual results','P0','Investigation'],
      ['Capture sanitized logs, environment details and failing inputs','P0','Investigation'],
      ['Trace the narrow code path and establish a reproducible failing test','P0','Diagnosis'],
      ['Identify the root cause with evidence, not guesses','P0','Diagnosis'],
      ['Implement the smallest safe patch with input and access checks','P0','Fix'],
      ['Prove the original failure passes and a nearby regression does not appear','P0','Verification'],
      ['Check accessibility and user-facing error recovery','P1','UX'],
      ['Document changed files, tests executed and remaining uncertainty','P1','Handover']
    ].map(([title,priority,phase],id)=>({id,title,priority,phase}));
  } else if (d.mode === 'Security review') {
    phases = [
      {title:'01 · Authorize and scope',description:'Identify owned code, trust boundaries, critical assets, user roles and explicitly permitted checks. Never run intrusive tests without authorization.'},
      {title:'02 · Threat model',description:'Map authentication, authorization, inputs, external dependencies, secrets and data movement to relevant OWASP controls.'},
      {title:'03 · Verify findings',description:'Use read-only static checks and authorized safe tests, inspect context and eliminate obvious false positives.'},
      {title:'04 · Prioritize remediation',description:'Document evidence, severity, confidence, fixes, retests and areas not examined. Never claim complete security.'}
    ];
    tasks = [
      ['Confirm authorized scope and exclude production credentials','P0','Scope'],
      ['Identify assets, roles, entry points and trust boundaries','P0','Threat model'],
      ['Review server-side authorization and object-level access','P0','Access control'],
      ['Review injection sinks, validation and output encoding','P0','Input security'],
      ['Check secret handling, dependency hygiene and TLS defaults','P0','Configuration'],
      ['Reproduce or validate each supported finding without invasive activity','P1','Verification'],
      ['Write redacted severity-ranked findings with confidence and evidence','P1','Reporting'],
      ['Define retests and explicitly note coverage gaps','P1','Handover']
    ].map(([title,priority,phase],id)=>({id,title,priority,phase}));
  } else if (d.mode === 'UI/UX improvement') {
    phases = [
      {title:'01 · Understand user journey',description:'Map the primary persona, current friction points, task success and mobile/desktop context without guessing analytics.'},
      {title:'02 · Improve information architecture',description:'Simplify hierarchy, navigation, actions and accessible form labels. Define consistent interaction states.'},
      {title:'03 · Build and compare',description:'Implement responsive changes in existing components, keeping keyboard behavior, content and design system consistent.'},
      {title:'04 · Usability verification',description:'Test representative tasks, small screens, keyboard, focus, error recovery and visual regression before release.'}
    ];
    tasks = [
      ['Describe target users, critical tasks and measurable UX success','P0','Discovery'],
      ['Capture existing friction points with actual observations','P0','Discovery'],
      ['Sketch revised information hierarchy and primary actions','P0','Design'],
      ['Specify mobile, empty, error, loading and success states','P0','Design'],
      ['Implement semantic, responsive and keyboard-friendly interactions','P0','Build'],
      ['Check contrast, labels, focus order and target sizes','P1','Accessibility'],
      ['Compare representative task completion and screenshots','P1','Verification'],
      ['Review authentication/privacy surfaces and release regressions','P1','Security']
    ].map(([title,priority,phase],id)=>({id,title,priority,phase}));
  } else if (d.mode === 'Performance review') {
    phases = [
      {title:'01 · Define performance baseline',description:'Choose target devices, workloads and metrics; gather actual timing and resource evidence first.'},
      {title:'02 · Locate bottlenecks',description:'Profile large assets, render paths, data access and network behavior; distinguish measured issues from hypotheses.'},
      {title:'03 · Improve one bottleneck',description:'Apply reversible targeted changes with correctness, access control and accessibility preserved.'},
      {title:'04 · Compare and guard',description:'Repeat the same measurements before/after with equivalent environments, regression tests and explicit limitations.'}
    ];
    tasks = [
      ['Specify performance metrics, device and representative workload','P0','Baseline'],
      ['Record baseline from a repeatable measurement method','P0','Baseline'],
      ['Profile the top bottleneck before changing source','P0','Analysis'],
      ['Implement a minimal targeted improvement','P0','Build'],
      ['Compare equivalent before/after runs including variance','P0','Verification'],
      ['Verify caching, access controls and privacy boundaries','P1','Security'],
      ['Check mobile UI, accessibility and behavior regressions','P1','UX'],
      ['Report actual impact, untested paths and safe rollback','P1','Handover']
    ].map(([title,priority,phase],id)=>({id,title,priority,phase}));
  }
  const ux=[
    {title:'Clear primary action',text:`Make the ${featureLabel} immediately discoverable, with one obvious next step and clear page hierarchy.`},
    {title:'Responsive by default',text:'Support narrow mobile screens, touch-friendly spacing, readable text and layouts without horizontal overflow.'},
    {title:'States that explain themselves',text:'Design skeleton/loading, empty, validation, permission, error and success states with useful recovery paths.'},
    {title:'Inclusive interactions',text:'Use semantic labels, visible focus, keyboard paths, sufficient contrast and accessible feedback.'},
    {title:'Trust & transparency',text:'Explain sensitive actions, confirmation, privacy choices and irreversible changes before users commit.'},
    {title:'Performance budget',text:'Avoid redundant fetches and oversized assets; measure key flows before claiming performance improvements.'},
  ];
  const acceptance = [
    {title:'Primary outcome',test:`A user can complete the ${featureLabel} with an observable result, including at least one failure/recovery path.`},
    {title:'Permissions',test:'Access to protected operations and data is enforced at a trusted boundary; unauthorized requests are rejected.'},
    {title:'Accessible interaction',test:d.type==='API / backend' ? 'API errors and successful results use documented, validated response schemas with actionable messages; no visual UI is assumed.' : 'Main flow works using keyboard where applicable and on a narrow viewport, with appropriate semantics and visible feedback.'},
    {title:'Automated verification',test:'Relevant success, failure and boundary cases have executable tests; results and gaps are reported accurately.'},
    {title:'Privacy and secrets',test:'Secrets are not committed or logged, user inputs are handled safely and sensitive data exposure is reviewed.'},
  ];
  const specific = {
    checkout:'Checkout totals, retry paths and confirmation are tested without double-charging or assuming payment success.',
    booking:'Conflicting times, unavailable slots and cancellation/error recovery are tested.',
    dashboard:'Data visibility respects user roles; empty, loading and stale-data views are understandable.',
    accounts:'Session expiry, password recovery, permissions and incorrect credentials have safe behavior.',
    catalog:'Search, filtering, empty results and product detail paths are tested.',
    messaging:'Message authorization, ordering, unread state and offline failures are tested.',
    delivery:'Location/status permission rules and delayed/unavailable tracking states are tested.',
    landing:'Primary action, navigation and mobile reading experience are tested.',
    core:'The principal flow is specified in observable steps with unambiguous success and failure conditions.'
  };
  acceptance.unshift({title:'Domain-specific verification',test:specific[focus] || specific.core});
  if(d.mode==='Fix a bug')acceptance.unshift({title:'Regression proof',test:'The reported issue fails before the patch and passes afterward under the same reproduction steps.'});
  if(d.mode==='Security review')acceptance.unshift({title:'Evidence-bound security review',test:'Each finding includes a redacted location, reproduction or rationale, confidence, severity and an authorized retest; untested areas are listed.'});
  if(d.mode==='UI/UX improvement')acceptance.unshift({title:'Task usability',test:'A representative critical task is compared before/after, and failure states remain reachable and accessible.'});
  if(d.mode==='Performance review')acceptance.unshift({title:'Measured comparison',test:'An equivalent before/after workload produces comparable measurements including variability and device assumptions.'});
  const openQuestions = [
    'Who is the main user and what result matters most?',
    'Which existing files, services, constraints or design system must remain unchanged?',
    'What test environment and success metric can verify the outcome?'
  ];
  if(d.mode==='Fix a bug')openQuestions.unshift('What exact steps reproduce the bug, and what should happen instead?');
  if(d.mode==='Security review')openQuestions.unshift('Which repositories, environments and checks are explicitly authorized?');
  if(d.mode==='UI/UX improvement')openQuestions.unshift('Which user task has the greatest measured or observed friction?');
  if(d.mode==='Performance review')openQuestions.unshift('What is the current measured baseline and target device/workload?');
  const riskNotes = [
    'Proposals are derived from this brief, not from inspecting a real repository.',
    'Never treat generated checks as proof of secure or accessible behavior.',
    'Obtain authorization before scanning real systems or changing production.'
  ];
  const requirements=[`Project: ${d.type} / ${d.stack} / ${d.platform}`,`Work mode: ${d.mode}`,`Target agent: ${d.agent}`,`Goal: ${cleanGoal}`,cleanConstraints?`Constraints: ${cleanConstraints}`:'',`Core focus: ${featureLabel}`].filter(Boolean);
  const fullPrompt=[
    'ROLE: Senior product engineer, UI/UX specialist, and defensive security reviewer.',
    ...requirements,'', 'IMPLEMENTATION PLAN:',
    ...phases.map((p,i)=>`${i+1}. ${p.title.replace(/^\d+ · /,'')}: ${p.description}`),'',
    'SUGGESTED FILES:',...files.map(f=>`- ${f.path} — ${f.purpose}`),'',
    'TASK BACKLOG:',...tasks.map((t,i)=>`${i+1}. [${t.priority}] ${t.title}`),'',
    'UI/UX CRITERIA:',...ux.map(x=>`- ${x.title}: ${x.text}`),'',
    'ACCEPTANCE CRITERIA:',...acceptance.map(x=>`- ${x.title}: ${x.test}`),'',
    'OPEN QUESTIONS (do not invent answers):',...openQuestions.map(x=>`- ${x}`),'',
    'VERIFICATION: Test inputs and authorization, run relevant unit/integration tests, check accessibility and mobile states, report measured evidence, blockers and untested areas.',
    'SECURITY: Do not expose secrets, never claim 100% security; require server-side authorization and safe failure behavior.',
    'RESPONSE FORMAT: Provide implementation steps, changed files, test evidence, remaining risks. Do not invent results.'
  ].join('\n');
  const specialist = d.mode === 'Security review' ? 'defensive application security reviewer' : d.mode === 'UI/UX improvement' ? 'product designer and frontend engineer' : d.mode === 'Performance review' ? 'performance engineer' : d.mode === 'Fix a bug' ? 'root-cause debugger' : 'software engineer';
  const shortPrompt=[
    `Act as a senior ${d.stack} ${specialist} with strong UX and application security practice.`,
    `Agent guidance: ${AGENT_GUIDANCE[d.agent]}`, 
    ...requirements,
    `Plan: ${phases.map(p=>p.title.replace(/^\d+ · /,'')).join(' → ')}.`,
    `Acceptance: ${acceptance.slice(0,d.detail==='Lean'?2:d.detail==='Balanced'?4:acceptance.length).map(x=>x.test).join(' ')}.`,
    `Deliver: ${tasks.slice(0,6).map(t=>t.title.replace(/[.]$/,'')).join('; ')}.`,
    `Starting files: ${files.slice(0,6).map(f=>f.path).join(', ')}.`,
    STANDARDS,
    'Use only authorized local checks. If the repository or reproduction details are missing, identify assumptions and request the minimum relevant context.',
    'Output concise steps, file changes, verification evidence and unresolved risks. No invented test results.'
  ].join('\n');
  return {input:d,focus,files,phases,tasks,ux,acceptance,openQuestions,riskNotes,fullPrompt,shortPrompt,sharedStandards:STANDARDS,createdAt:new Date().toISOString()};
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
    {name:'Acceptance tests',pass:project.acceptance?.length>=6 && project.acceptance.every(x=>x.test.length>15),detail:'Includes testable outcomes and a domain-specific scenario.'},
    {name:'Evidence boundaries',pass:project.riskNotes?.length>=2 && project.openQuestions?.length>=3,detail:'Clearly identifies assumptions and unverified areas.'},
    {name:'UX and accessible interactions',pass:project.ux.length>=4 && (/keyboard|accessible/i.test(prompt) || (reuse && sharedSent)),detail:'Covers responsive, keyboard and interaction states.'},
    {name:'Security and test coverage',pass:/authorization|permissions/i.test(prompt)&&/test/i.test(prompt),detail:'Retains authorization and verification responsibilities.'},
    {name:'Context reuse safety',pass:!reuse || sharedSent,detail:'References are used only after shared standards have been sent to the same AI conversation.'},
  ];
  return tests.map(t=>({...t,status:t.pass?'pass':'fail'}));
}
export function exportMarkdown(project,prompt,tests) {
  const d=project.input;
  return [`# Kattour Guardian · ${d.type}`,``, `**Stack:** ${d.stack}  `,`**Platform:** ${d.platform}  `,`**Work mode:** ${d.mode}  `,`**Target agent:** ${d.agent}  `,`**Detail:** ${d.detail}  `,`**Goal:** ${redact(d.goal)}`, d.constraints?`**Constraints:** ${redact(d.constraints)}`:'',``,`## Execution plan`,...project.phases.map(x=>`- **${x.title}** — ${x.description}`),``,`## Proposed file tree`, '```text', ...project.files.map(x=>x.path),'```','',`## Tasks`,...project.tasks.map(t=>`- [ ] **${t.priority}** ${t.title}`),'',`## UI/UX recommendations`,...project.ux.map(x=>`- **${x.title}:** ${x.text}`),'',`## Quality gate`,...tests.map(t=>`- ${t.status==='pass'?'PASS':'FAIL'} · ${t.name}`),'',`## Optimized prompt`,'```text',prompt,'```','',`*Generated offline from deterministic templates. Inspect and adapt before production use.*`].filter(x=>x!==undefined).join('\n');
}
export function exportJSON(project,prompt,tests) {
  return JSON.stringify({schema:'kattour-guardian-playground/1.1',input:{...project.input,goal:redact(project.input.goal),constraints:redact(project.input.constraints)},focus:project.focus,phases:project.phases,files:project.files,tasks:project.tasks,ux:project.ux,acceptance_criteria:project.acceptance,open_questions:project.openQuestions,risk_notes:project.riskNotes,optimized_prompt:prompt,quality_checks:tests.map(({name,status,detail})=>({name,status,detail})),token_estimates:{baseline:estimateTokens(project.fullPrompt),optimized:estimateTokens(prompt),method:'characters / 4; not a model tokenizer'},created_at:project.createdAt},null,2);
}

/** Opt-in share format: the full brief is in a URL fragment, not server query parameters. */
export function encodeShareBrief(raw, baseUrl) {
  const d=normalizedInput(raw);
  if(containsSecrets(d.goal+'\n'+d.constraints))throw new Error('Remove secrets before sharing.');
  if(d.goal.length<18)throw new Error('Enter a more specific goal first.');
  const url=new URL(baseUrl);
  if(!['https:','http:'].includes(url.protocol)||url.username||url.password)throw new Error('A public HTTP(S) URL is required.');
  url.search='';url.hash='';
  const encoded=encodeURIComponent(JSON.stringify({v:1,input:d}));
  const result=url.toString()+'#brief='+encoded;
  if(result.length>2300)throw new Error('Brief too long for a share link; export JSON instead.');
  return result;
}
export function decodeShareBrief(fragment) {
  if(typeof fragment!=='string'||fragment.length>2300||!fragment.startsWith('#brief='))throw new Error('Unsupported shared brief');
  const raw=JSON.parse(decodeURIComponent(fragment.slice(7)));
  if(!raw||raw.v!==1||!raw.input||typeof raw.input!=='object'||Array.isArray(raw.input))throw new Error('Invalid shared brief');
  for(const k of ['goal','constraints'])if(raw.input[k]!==undefined&&typeof raw.input[k]!=='string')throw new Error('Invalid brief fields');
  const d=normalizedInput(raw.input);
  if(d.goal.length<18||containsSecrets(d.goal+'\n'+d.constraints))throw new Error('Unsafe or incomplete shared brief');
  return d;
}
