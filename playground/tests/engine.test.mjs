import test from 'node:test';
import assert from 'node:assert/strict';
import {PROJECT_TYPES,STACKS,PRESETS,TARGET_AGENTS,WORK_MODES,DETAIL_LEVELS,normalizedInput,generateProject,optimizedPrompt,buildQA,redact,containsSecrets,isCompatible,estimateTokens,percentReduction,exportMarkdown,exportJSON} from '../src/engine.mjs';
const brief={type:'Web application',stack:'Next.js + TypeScript',platform:'Web',goal:'Build a secure, responsive analytics dashboard with role-based access and accessible charts.',constraints:'EU data handling and a low dependency footprint.'};
test('builds a meaningful project plan, tasks, UX suggestions and files',()=>{const p=generateProject(brief);assert.equal(p.phases.length,4);assert.ok(p.tasks.length>=8);assert.ok(p.ux.length>=5);assert.ok(p.files.some(f=>f.path.includes('tsx')));});
test('stack-based file architecture responds to framework',()=>{assert.ok(generateProject({...brief,stack:'Flutter',type:'Mobile application',platform:'iOS + Android'}).files.some(f=>f.path==='lib/main.dart'));assert.ok(generateProject({...brief,stack:'Vue + Nuxt'}).files.some(f=>f.path.endsWith('.vue')));assert.ok(generateProject({...brief,stack:'FastAPI + Python',type:'API / backend'}).files.some(f=>f.path==='app/main.py'));});
test('optimizes context while preserving goal and security expectations',()=>{const p=generateProject(brief);const slim=optimizedPrompt(p);assert.ok(slim.length<p.fullPrompt.length);assert.ok(slim.includes(brief.goal));assert.match(slim,/server-side authorization/i);assert.match(slim,/automated tests/i);assert.ok(estimateTokens(slim)<estimateTokens(p.fullPrompt));});
test('reuse only allowed after shared standards are declared sent',()=>{const p=generateProject(brief);const unsafe=optimizedPrompt(p,{reuse:true,sharedSent:false});assert.match(unsafe,/KG-C1: Preserve/);assert.ok(buildQA(p,unsafe,{reuse:true,sharedSent:false}).some(t=>t.status==='fail'));const safe=optimizedPrompt(p,{reuse:true,sharedSent:true});assert.ok(safe.includes('previously supplied KG-C1'));assert.ok(buildQA(p,safe,{reuse:true,sharedSent:true}).every(t=>t.status==='pass'));});
test('redacts credential-like values from generated export and blocks preflight',()=>{const input={...brief,goal:'Build a secure dashboard, api_key: ABCDEFGHIJKLMNOP, include monthly reports.'};const p=generateProject(input);assert.equal(containsSecrets(input.goal),true);assert.ok(!p.fullPrompt.includes('ABCDEFGHIJKLMNOP'));assert.ok(p.fullPrompt.includes('[REDACTED]'));assert.ok(buildQA(p,optimizedPrompt(p)).some(x=>x.name==='Secrets excluded'&&x.status==='fail'));assert.ok(!exportJSON(p,optimizedPrompt(p),[]).includes('ABCDEFGHIJKLMNOP'));});
test('rejects incompatible project configurations',()=>{assert.equal(isCompatible(normalizedInput({...brief,type:'API / backend',platform:'iOS'})),false);assert.ok(buildQA(generateProject({...brief,type:'API / backend',platform:'iOS'}),'authorization tests').some(x=>x.name==='Supported configuration'&&x.status==='fail'));});
test('has project type and stack choices and presets',()=>{assert.ok(PROJECT_TYPES.length>=4);assert.ok(STACKS.length>=8);assert.ok(PRESETS.length>=3);});
test('exports Markdown and machine-readable JSON',()=>{const p=generateProject(brief),prompt=optimizedPrompt(p),tests=buildQA(p,prompt),md=exportMarkdown(p,prompt,tests);assert.match(md,/## Execution plan/);assert.match(md,/## Proposed file tree/);const json=JSON.parse(exportJSON(p,prompt,tests));assert.equal(json.input.stack,brief.stack);assert.equal(json.quality_checks.length,10);});
test('token percentage is only an arithmetic comparison',()=>{assert.equal(percentReduction(1000,250),75);assert.equal(percentReduction(0,0),0);assert.equal(estimateTokens('a'.repeat(9)),3);});
test('normalizes invalid input safely',()=>{const d=normalizedInput({type:'invalid',stack:'invalid',platform:'invalid',goal:' hi '});assert.equal(d.type,'Web application');assert.equal(d.goal,'hi');assert.equal(d.stack,'Next.js + TypeScript');});
test('five work modes produce distinct evidence-based workflows',()=>{
  const modes=['Build feature','Fix a bug','Security review','UI/UX improvement','Performance review'];
  const first=new Set();
  for(const mode of modes){
    const p=generateProject({...brief,mode});
    assert.equal(p.input.mode,mode);
    assert.equal(p.phases.length,4);
    assert.ok(p.tasks.length>=8);
    assert.ok(p.acceptance.length>=6);
    assert.ok(p.openQuestions.length>=3);
    first.add(p.phases[0].title);
    const slim=optimizedPrompt(p);
    assert.match(slim,/authorized local checks/i);
    assert.ok(slim.length<p.fullPrompt.length);
    assert.equal(buildQA(p,slim).filter(x=>x.status==='fail').length,0);
  }
  assert.equal(first.size,5);
});
test('specialized mode includes root-cause or authorized security guardrails',()=>{
  const fix=generateProject({...brief,mode:'Fix a bug',agent:'Claude Code',detail:'Lean'});
  assert.match(optimizedPrompt(fix),/root-cause debugger/i);
  assert.match(optimizedPrompt(fix),/Claude|Explore relevant code/i);
  assert.match(fix.tasks.map(x=>x.title).join('\n'),/reproducible failing test/i);
  const sec=generateProject({...brief,mode:'Security review',detail:'Thorough'});
  assert.match(sec.phases[0].description,/authorization|authorized|permitted/i);
  assert.match(sec.acceptance[0].test,/redacted location/i);
});
test('agent-specific prompts are distinct and defensively scoped',()=>{
  assert.equal(TARGET_AGENTS.length,6);
  assert.equal(WORK_MODES.length,5);
  assert.equal(DETAIL_LEVELS.length,3);
  const prompts=TARGET_AGENTS.map(agent=>optimizedPrompt(generateProject({...brief,agent})));
  assert.equal(new Set(prompts).size,TARGET_AGENTS.length);
  for(const p of prompts){assert.match(p,/No invented test results/);assert.match(p,/authorized local checks/i);}
});
test('higher detail means more acceptance evidence and exports preserve project mode',()=>{
  const lean=optimizedPrompt(generateProject({...brief,detail:'Lean'}));
  const thorough=optimizedPrompt(generateProject({...brief,detail:'Thorough'}));
  assert.ok(lean.length<thorough.length);
  const p=generateProject({...brief,mode:'UI/UX improvement',agent:'Cursor',detail:'Thorough'});
  const j=JSON.parse(exportJSON(p,optimizedPrompt(p),buildQA(p,optimizedPrompt(p))));
  assert.equal(j.schema,'kattour-guardian-playground/1.1');
  assert.equal(j.input.mode,'UI/UX improvement');
  assert.equal(j.input.agent,'Cursor');
  assert.equal(j.input.detail,'Thorough');
  assert.equal(j.acceptance_criteria.length,7);
});
test('redacts common provider and GitHub tokens and refuses to mark them clean',()=>{
  const token='ghp_'+('A'.repeat(36));
  assert.equal(containsSecrets(token),true);
  assert.equal(redact('token is '+token).includes(token),false);
  const p=generateProject({...brief,goal:brief.goal+' '+token});
  assert.ok(!p.fullPrompt.includes(token));
  assert.ok(buildQA(p,optimizedPrompt(p)).some(x=>x.name==='Secrets excluded'&&x.status==='fail'));
});
test('share links round trip safely without server query strings',async()=>{
 const {encodeShareBrief,decodeShareBrief}=await import('../src/engine.mjs');
 const input={...brief,mode:'Fix a bug',agent:'Cursor',detail:'Thorough'};
 const u=encodeShareBrief(input,'https://eliaskatt.github.io/kattour-guardian/?utm_source=example');
 assert.match(u,/^https:\/\/eliaskatt\.github\.io\/kattour-guardian\/#brief=/);
 const parsed=new URL(u);assert.equal(parsed.search,'');
 const recovered=decodeShareBrief(parsed.hash);assert.equal(recovered.mode,'Fix a bug');assert.equal(recovered.agent,'Cursor');assert.equal(recovered.goal,brief.goal);
});
test('unsafe secrets and oversized share links are blocked',async()=>{
 const {encodeShareBrief,decodeShareBrief}=await import('../src/engine.mjs');
 assert.throws(()=>encodeShareBrief({...brief,goal:brief.goal+' '+('ghp_'+'A'.repeat(36))},'https://example.test/'),/secrets/);
 assert.throws(()=>encodeShareBrief({...brief,goal:'x'.repeat(4000)},'https://example.test/'),/too long/);
 assert.throws(()=>decodeShareBrief('#brief='+encodeURIComponent(JSON.stringify({v:1,input:{goal:'password: VERYSECRETISNOTOK'}}))),/Unsafe|incomplete/);
 assert.throws(()=>decodeShareBrief('#brief=not-json'),SyntaxError);
});
