// Browser-independent logic smoke tests. Not a substitute for visual browser QA.
import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const root=new URL('../',import.meta.url),html=fs.readFileSync(new URL('outputs/dashboard.html',root),'utf8');
const payload=html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const script=html.match(/<\/script><script>([\s\S]*?)<\/script>/)[1];
class El{constructor(){this.value='';this.options=[];this.children=[];this.innerHTML='';this.textContent='';this.className=''}add(o){this.options.push(o)}replaceChildren(...a){this.children=[...a];this.options=[...a];this.value=a[0]?.value||''}append(a){this.children.push(a)}setAttribute(){}click(){}}
const els={};for(const id of ['data','sector','period','partner','location','cards','unit','trend','map','reset','followup','download','print','reports','dq','facilities'])els[id]=new El();els.data.textContent=payload;els.sector.value='Education';
const context=vm.createContext({document:{getElementById:id=>els[id],createElement:()=>new El()},Option:function(text,value){this.text=text;this.value=value},window:{print(){}},Blob,URL,setTimeout});
vm.runInContext(script,context);let checks=0;
function check(name,fn){fn();console.log('PASS '+name);checks++}
check('Default sector has expected SQL totals',()=>{assert.match(els.cards.innerHTML,/83,916/);assert.match(els.cards.innerHTML,/142 \/ 144/)});
check('All twelve fictional locations displayed',()=>assert.equal(els.map.children.length,12));
els.sector.value='WASH';els.sector.onchange();
check('Sector filter and partner list refresh',()=>{assert.match(els.cards.innerHTML,/78,191/);assert.deepEqual(els.partner.options.map(o=>o.value),['','P03','P04'])});
els.period.value='2026-09';els.period.onchange();
check('Period filter retains missing and rejected reports',()=>{assert.match(els.followup.textContent,/24 expected reports/);assert.match(els.reports.innerHTML,/Needs correction/)});
els.partner.value='P04';els.partner.onchange();els.location.value='L08';els.location.onchange();
check('Combined filters retain one expected report',()=>assert.match(els.followup.textContent,/1 expected reports/));
check('Filtered CSV preserves synthetic label and source grain',()=>{const csv=vm.runInContext('csv()',context);assert.equal(csv.split('\n').length,2);assert.match(csv,/Synthetic demonstration/);assert.match(csv,/2026-09/) });
els.reset.onclick();
check('Reset restores default filters and totals',()=>{assert.equal(els.sector.value,'Education');assert.equal(els.period.value,'');assert.match(els.cards.innerHTML,/83,916/)});
check('Facility snapshot freshness disclosure visible in HTML',()=>assert.match(html,/16 days old/));
console.log(`${checks} dashboard logic checks passed. Browser visual QA is unverified.`);
