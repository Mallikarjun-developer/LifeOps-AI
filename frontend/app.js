const $=id=>document.getElementById(id);
const escapeHTML=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let tasks=[],busy=false;
$('date').textContent=new Date().toLocaleDateString(undefined,{weekday:'short',month:'short',day:'numeric'});
async function request(path,opts={}){const r=await fetch('/api'+path,{...opts,headers:{'Content-Type':'application/json',...(opts.headers||{})}});const body=await r.json();if(!r.ok)throw Error(body.detail||'Request failed');return body;}
async function refresh(){tasks=await request('/tasks');$('total').textContent=tasks.length;$('done').textContent=tasks.filter(t=>t.status==='done').length;$('high').textContent=tasks.filter(t=>t.priority==='high'&&t.status!=='done').length;$('scheduled').textContent=tasks.filter(t=>t.scheduled_start&&t.status!=='done').length;const list=$('taskList');list.innerHTML=tasks.length?'':`<div class="empty">No tasks yet. Add one or ask LifeOps to create it.</div>`;tasks.forEach(t=>{const el=document.createElement('div');el.className='task '+(t.status==='done'?'done':'');el.innerHTML=`<input type="checkbox" ${t.status==='done'?'checked':''} aria-label="Complete task"><div class="task-content"><div class="task-title">${escapeHTML(t.title)}</div><div class="task-meta">${t.due?'Due '+escapeHTML(t.due.replace('T',' '))+' · ':''}${t.duration} min · Task #${t.id}</div></div><span class="pill ${escapeHTML(t.priority)}">${escapeHTML(t.priority)}</span><button class="delete" title="Delete task" aria-label="Delete task">×</button>`;el.querySelector('input').addEventListener('change',async e=>{try{await request('/tasks/'+t.id,{method:'PATCH',body:JSON.stringify({status:e.target.checked?'done':'todo'})});await refresh()}catch(err){alert(err.message)}});el.querySelector('.delete').addEventListener('click',async()=>{if(!confirm('Delete this task?'))return;try{await request('/tasks/'+t.id,{method:'DELETE'});await refresh()}catch(err){alert(err.message)}});list.appendChild(el)});const slots=tasks.filter(t=>t.scheduled_start&&t.status!=='done').sort((a,b)=>a.scheduled_start.localeCompare(b.scheduled_start));$('schedule').innerHTML=slots.length?slots.map(t=>`<div class="slot"><span class="slot-time">${escapeHTML(t.scheduled_start.slice(11,16))}–${escapeHTML(t.scheduled_end.slice(11,16))}</span><span class="slot-title">${escapeHTML(t.title)}</span></div>`).join(''):'<div class="empty">Select “Replan my day” to generate a schedule.</div>';}
function append(role,text){const el=document.createElement('div');el.className='message '+role;el.innerHTML=(role==='assistant'?'<div class="avatar">✦</div>':'')+'<div class="bubble"></div>';el.querySelector('.bubble').textContent=text;$('chat').appendChild(el);$('chat').scrollTop=$('chat').scrollHeight;}
function speak(text){if(!$('speakToggle').checked||!('speechSynthesis' in window))return;window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);u.lang='en-US';u.rate=1.03;window.speechSynthesis.speak(u)}
async function send(message){message=message.trim();if(!message||busy)return;busy=true;$('message').value='';append('user',message);$('voiceStatus').textContent='LifeOps is thinking and using tools…';try{const result=await request('/chat',{method:'POST',body:JSON.stringify({message})});append('assistant',result.reply);speak(result.reply);await refresh();if(result.action==='plan'&&result.details?.conflicts?.length){$('conflicts').innerHTML='<div class="warning">⚠ '+result.details.conflicts.map(c=>escapeHTML(c.title)+': '+escapeHTML(c.reason)).join('<br>')+'</div>';}else if(result.action==='plan')$('conflicts').innerHTML='';}catch(err){append('assistant','Connection error: '+err.message+'. Make sure both servers are running.')}finally{busy=false;$('voiceStatus').textContent='Press the microphone to speak'}}
$('chatForm').addEventListener('submit',e=>{e.preventDefault();send($('message').value)});document.querySelectorAll('[data-command]').forEach(b=>b.addEventListener('click',()=>send(b.dataset.command)));
$('addBtn').addEventListener('click',()=>$('taskForm').classList.toggle('hidden'));
$('taskForm').addEventListener('submit',async e=>{e.preventDefault();try{await request('/tasks',{method:'POST',body:JSON.stringify({title:$('newTitle').value,priority:$('newPriority').value,due:$('newDue').value})});$('taskForm').reset();$('taskForm').classList.add('hidden');await refresh()}catch(err){alert(err.message)}});
$('planBtn').addEventListener('click',()=>send('Plan my day'));
const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
if(!Recognition){$('voiceStatus').textContent='Voice recognition is unavailable in this browser. Use Chrome or type below.';$('micBtn').title='Speech recognition unavailable';$('micBtn').disabled=true}else{$('micBtn').addEventListener('click',()=>{const r=new Recognition();r.lang='en-US';r.interimResults=false;r.maxAlternatives=1;r.onstart=()=>{$('micBtn').classList.add('listening');$('voiceStatus').textContent='Listening…';$('voiceStatus').classList.add('listening')};r.onend=()=>{$('micBtn').classList.remove('listening');$('voiceStatus').classList.remove('listening')};r.onerror=e=>{$('voiceStatus').textContent='Microphone error: '+e.error};r.onresult=e=>send(e.results[0][0].transcript);try{r.start()}catch(e){$('voiceStatus').textContent=e.message}})}
request('/health').then(()=>{$('connection').textContent='API ready · checking MCP…';return refresh()}).then(()=>{$('connection').textContent='API + MCP online'}).catch(()=>{$('connection').textContent='Offline — start both servers';append('assistant','The backend is offline. See README.md for startup instructions.')});


/* Navigation: three real views, while preserving existing dashboard features. */
function navigateLifeOps() {
  const validViews = new Set(['overview', 'tasks', 'assistant']);
  const requested = window.location.hash.slice(1).toLowerCase();
  const view = validViews.has(requested) ? requested : 'overview';

  document.body.dataset.view = view;
  document.querySelectorAll('.sidebar nav a[href^="#"]').forEach(link => {
    const active = link.getAttribute('href') === '#' + view;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });

  const heading = document.querySelector('header h1');
  const subtitle = document.querySelector('header .sub');
  const titles = {
    overview: ['Take control of your day ✦', 'Turn intentions into actions. Speak, plan, and adapt in real time.'],
    tasks: ['Your tasks & schedule ✦', 'Organize priorities, manage deadlines, and replan your day.'],
    assistant: ['Your voice assistant ✦', 'Speak or type to let LifeOps manage your day through MCP tools.']
  };
  if (heading) heading.textContent = titles[view][0];
  if (subtitle) subtitle.textContent = titles[view][1];
  window.scrollTo({ top: 0, behavior: 'instant' });
}
window.addEventListener('hashchange', navigateLifeOps);
navigateLifeOps();
