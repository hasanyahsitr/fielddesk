'use strict';
const $ = selector => document.querySelector(selector);
const token = $('meta[name="atolye-token"]').content;
let historyMode=false, preferencesLoaded=false;
let state, view = 'home', filter = 'Tümü', history = [], activeJob = null, finishedJob = null, toastTimer;
const titles = {home:'Genel bakış',apps:'Uygulamalar',workflows:'İş akışları',setup:'Çanta hazırlığı',chat:'Asistan',library:'Bilgi merkezi',projects:'Projeler',archive:'Kurulum arşivi',system:'Sistem ve yedek'};
const esc = value => String(value ?? '').replace(/[&<>"']/g,c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const searchText = value => String(value??'').normalize('NFKD').replace(/\p{M}/gu,'').toLowerCase().replace(/ı/g,'i');
const num = value => Number(value).toLocaleString(uiLocale());
function toast(message) { clearTimeout(toastTimer); $('#toast').textContent=message; $('#toast').hidden=false; toastTimer=setTimeout(()=>$('#toast').hidden=true,6500); }
async function api(url,data) {
  const options = data === undefined ? {headers:{'X-Atolye-Token':token}} : {method:'POST',headers:{'Content-Type':'application/json','X-Atolye-Token':token},body:JSON.stringify(data)};
  const response=await fetch(url,options), payload=await response.json();
  if(!response.ok) throw new Error(payload.message || 'İşlem tamamlanamadı.');
  return payload;
}
function navigate(name) {
  if(!titles[name]) name='home'; const changed=view!==name;view=name;
  document.querySelectorAll('.view').forEach(x=>x.hidden=x.id!=='view-'+name);
  document.querySelectorAll('nav button').forEach(x=>{x.classList.toggle('active',x.dataset.view===name); x.setAttribute('aria-current',x.dataset.view===name?'page':'false');});
  $('#page-title').textContent=titles[name];
  if(changed)window.scrollTo(0,0);
  if(location.hash!=='#'+name) location.hash=name;
}
function card(item) {
  const favorite=state.favorites.includes(item.id);
  const initials=item.name.replace(/[^\p{L}\p{N} ]/gu,'').split(/\s+/).filter(Boolean).slice(0,2).map(x=>x[0]).join('').toLocaleUpperCase('tr');
  return `<article class="app-card ${item.ready?'':'unavailable'}"><div class="app-icon" aria-hidden="true">${esc(initials)}</div><div class="app-info"><h3 ${item.custom?'data-user-content':''}>${esc(item.name)}</h3><p ${item.custom?'data-user-content':''}>${esc(item.description)}</p>${item.custom?`<button class="remove-app text-button" data-remove-app="${esc(item.id)}">Menüden kaldır</button>`:''}</div><div class="app-meta"><span class="category-tag">${esc(item.category)}</span><small>${item.type==='app'?'Uygulama':item.type==='terminal'?'Terminal':'Klasör'}</small></div><div class="app-actions"><button class="star-button ${favorite?'selected':''}" data-favorite="${esc(item.id)}" aria-label="${favorite?'Favorilerden çıkar':'Favorilere ekle'}: ${esc(item.name)}" aria-pressed="${favorite}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9z"/></svg></button><button class="launch-button" aria-label="${esc(item.name)}: ${item.ready?'aç':'dosya eksik'}" data-open="${esc(item.id)}" ${item.ready?'':'disabled'}>${item.ready?'Aç':'Eksik'}</button></div></article>`;
}
function renderApps() {
  const focused=document.activeElement, gridId=focused.closest('.app-grid')?.id;
  const favoriteId=focused.dataset.favorite, focusedFilter=focused.dataset.filter;
  const q=searchText($('#app-search').value);
  const rows=state.entries.filter(x=>(filter==='Tümü'||filter==='Favoriler'&&state.favorites.includes(x.id)||x.category===filter) && searchText([x.name,x.description,x.category,t(x.name),t(x.description),t(x.category)].join(' ')).includes(q));
  $('#apps-count').textContent=rows.length+' öğe'+(q||filter!=='Tümü'?' · filtrelenmiş':'');
  $('#apps-grid').innerHTML=rows.map(card).join('')||'<div class="empty-state">Bu aramada uygulama bulunamadı.</div>';
  const favorites=state.entries.filter(x=>x.ready&&state.favorites.includes(x.id));
  const defaults=['vscode','libreoffice-app','krita','vlc'].map(id=>state.entries.find(x=>x.id===id)).filter(x=>x?.ready);
  const quick=[...favorites,...defaults.filter(x=>!favorites.some(f=>f.id===x.id))].slice(0,4);
  $('#quick-grid').innerHTML=quick.map(card).join('')||'<div class="empty-state">Çantana araç eklediğinde burada görünür.</div>';
  $('#app-filters').innerHTML=['Tümü','Favoriler',...new Set(state.entries.map(x=>x.category))].map(x=>`<button class="${x===filter?'active':''}" data-filter="${esc(x)}" aria-pressed="${x===filter}">${esc(x)}</button>`).join('');
  if(gridId&&favoriteId)for(const b of $('#'+gridId).querySelectorAll('[data-favorite]'))if(b.dataset.favorite===favoriteId)b.focus({preventScroll:true});
  if(focusedFilter)for(const b of document.querySelectorAll('[data-filter]'))if(b.dataset.filter===focusedFilter)b.focus({preventScroll:true});
}
function renderProjects() {
  $('#projects-grid').innerHTML=state.projects.map(x=>`<article class="project-card"><div class="eyebrow">${esc(x.kind)} / ${x.code?'KOD ÇALIŞMA ALANI':'KLASÖR'}</div><h3>${esc(x.name)}</h3><p>${esc(x.path)}</p><div class="project-actions"><button class="primary" data-project="${esc(x.id)}" data-editor="true">VS Code’da aç ↗</button><button class="secondary" data-project="${esc(x.id)}">Klasör ↗</button></div></article>`).join('')||'<div class="empty-state">04_PROJELER klasörüne bir proje eklediğinde burada görünür.</div>';
}
function renderArchive() {
  const q=$('#archive-query').value.toLocaleLowerCase('tr');
  let note='Dosyalar arşivdir; tek tıkla sistem kurulumu yapılmaz. Bir ISO’yu saklamak diski önyüklenebilir yapmaz.';
  if(state.packages.some(x=>x.id==='windows10-mct'&&x.ready)&&!state.packages.some(x=>x.ready&&x.path.toLowerCase().includes('windows10')&&x.path.toLowerCase().endsWith('.iso')))note+=' Windows 10 için medya oluşturma aracı var, ISO henüz yok.';
  if(state.packages.some(x=>x.id==='acronis-trial'&&x.ready))note+=' Acronis paketi denemedir.';
  $('#archive-note').textContent=note;
  $('#archive-body').innerHTML=state.packages.filter(x=>(x.name+' '+x.category).toLocaleLowerCase('tr').includes(q)).map(x=>`<tr><td>${esc(x.name)}<small>${esc(x.version)}</small></td><td>${esc(x.category)}</td><td>${x.bytes?num(Math.round(x.bytes/1e6))+' MB':'—'}</td><td><span class="${x.ready?'ok':'missing'}">${esc(x.status)}</span><small>${esc(x.verification||'Doğrulama kaydı yok')}</small></td><td><button class="launch-button" data-package="${esc(x.id)}" ${x.ready?'':'disabled'}>Klasör ↗</button></td></tr>`).join('')||'<tr><td colspan="5">Eşleşen paket bulunamadı.</td></tr>';
}
function renderLibraryStatus(status) {
  $('#library-status').textContent=status.running?`Dizin güncelleniyor · ${num(status.seen||0)} dosya tarandı`:`${num(status.files)} dosya · ${num(status.chunks)} metin bölümü`;
  $('#index-library').disabled=status.running;
  const errors=status.errors||[];
  $('#library-errors').hidden=!errors.length;
  $('#library-errors').innerHTML=errors.length?`<summary>${num(errors.length)} belge okunamadı · Listeyi göster</summary><p>Bu belgeler arama sonuçlarına eklenmedi. Dosya biçimini ve açılabilirliğini kontrol et.</p><ul>${errors.slice(0,20).map(x=>`<li>${esc(x.path)}</li>`).join('')}</ul>`:'';
}
function renderState() {
  $('#version').textContent=state.version;
  $('#workspace-root').textContent=state.root;
  const apps=state.entries.filter(x=>x.type==='app'&&x.ready).length;
  $('#nav-count').textContent=apps; $('#stat-apps').textContent=num(apps);
  $('#stat-models').textContent=state.models.filter(x=>x.ready).length;
  $('#stat-files').textContent=num(state.library.files);
  $('#stat-disk').textContent=(state.device.free_disk_gb/1000).toLocaleString(uiLocale(),{minimumFractionDigits:2,maximumFractionDigits:2})+' TB';
  $('#stat-archive').textContent=state.archive_gb+' GB paket ve model arşivi';
  const backed=state.backup.completed;
  $('#home-backup-title').textContent=backed?'Son yedek tamamlandı':'Yedek kaydı yok';
  $('#home-backup-text').textContent=backed?'Son kayıt: '+new Date(state.backup.date).toLocaleString(uiLocale()):'İkinci diske fiziksel yedek henüz tamamlanmadı. Tanımlı yedek diskini bağladığında hazır.';
  $('#backup-detail').textContent=backed?'Son başarılı kayıt: '+new Date(state.backup.date).toLocaleString(uiLocale()):'Henüz başarılı fiziksel yedek kaydı yok. İkinci diskin bağlanması ve tanımlanması gerekiyor.';
  const currentModel=$('#model-select').value;
  $('#model-select').innerHTML=state.models.map(x=>`<option value="${esc(x.id)}" ${x.ready?'':'disabled'}>${esc(x.name)}${x.ready?'':' · dosya eksik'}</option>`).join('');
  $('#model-select').value=currentModel|| (state.models.find(x=>x.id==='gemma-e2b'&&x.ready)?.id || state.models.find(x=>x.ready)?.id || 'gemma-e2b');
  $('#model-status').textContent=state.model?state.models.find(x=>x.id===state.model)?.name+' · başlatılmış':'Gerektiğinde başlar';
  const d=state.device;
  $('#system-grid').innerHTML=[['BU BİLGİSAYAR',d.architecture,d.system],['BELLEK',d.ram_gb+' GB',d.available_ram_gb+' GB kullanılabilir RAM'],['ÇANTANIN DİSKİ',num(d.free_disk_gb)+' GB boş',state.root]].map(x=>`<article class="system-card"><span class="eyebrow">${esc(x[0])}</span><h3>${esc(x[1])}</h3><p>${esc(x[2])}</p></article>`).join('');
  renderApps();renderProjects();renderArchive();renderLibraryStatus(state.library);
  document.dispatchEvent(new CustomEvent('atolye-state'));
}
async function refresh() { state=await api('/api/state'); if(!preferencesLoaded){preferencesLoaded=true;setUILanguage(state.preferences?.language||'en');} renderState(); if(state.job) updateJob(state.job); }
function sourceMarkup(sources) {
  if(!sources?.length) return '';
  return `<div class="sources"><span class="message-label">GETİRİLEN YEREL KAYNAKLAR · ALINTILARI KONTROL ET</span>${sources.map((x,i)=>`<details><summary class="result-path" data-user-content>[${i+1}] ${esc(x.title)}</summary><p class="fine-print">${esc(x.path)}</p><pre class="message-body">${esc(x.excerpt)}</pre><button data-file="${esc(x.path)}">Dosyayı aç ↗</button></details>`).join('')}</div>`;
}
function appendMessage(role,content,sources=[]) {
  $('.chat-welcome')?.remove();
  const el=document.createElement('article');el.className='chat-message '+role;
  el.innerHTML=`<span class="message-label">${role==='user'?'SEN':'FieldDesk / '+esc(activeJob?.provider&&activeJob.provider!=='local'?activeJob.provider.toUpperCase():'YEREL ASİSTAN')}</span><div class="message-body" data-user-content>${esc(content)}</div>${sourceMarkup(sources)}`;
  $('#chat-thread').append(el);$('#chat-thread').scrollTop=$('#chat-thread').scrollHeight;
}
function setBusy(busy) { $('#chat-send').disabled=busy;$('#model-select').disabled=busy;$('#clear-chat').disabled=busy;$('#use-documents').disabled=busy;$('#chat-progress').classList.toggle('busy',busy);for(const node of document.querySelectorAll('#provider-select,#cloud-model,#provider-form input,#provider-form select,#provider-form button,.provider-actions button'))node.disabled=busy; }
function updateJob(job) {
  if(activeJob?.id!==job.id&&!$('.chat-message'))appendMessage('user',job.question);
  activeJob=job;const busy=['loading','generating'].includes(job.status);
  const cloud=job.provider&&job.provider!=='local';
  const modelName=cloud?job.model:state?.models.find(x=>x.id===job.model)?.name||'Yerel model';
  $('#model-status').textContent=job.status==='loading'?modelName+' · bağlanıyor':job.status==='generating'||job.status==='complete'?modelName+(cloud?' · API':' · başlatılmış'):job.status==='cancelled'?'Durduruldu':'Yanıt hatası';
  setBusy(busy);$('#chat-progress').hidden=false;$('#chat-progress').textContent=job.message+(job.usage?' · Kullanım: '+Object.entries(job.usage).map(([k,v])=>k+': '+v).join(', '):'');
  if(!busy&&finishedJob!==job.id) {
    finishedJob=job.id;
    if(job.status==='complete') { appendMessage('assistant',job.answer,job.sources);if(!job.documents) history.push({role:'assistant',content:job.answer}); }
    if(job.status==='error') toast(job.message);
  }
}
async function submitChat() {
  if(connectionBusy)return;
  const question=$('#chat-input').value.trim();if(!question) return;
  if(activeJob&&['loading','generating'].includes(activeJob.status)) return;
  setBusy(true);
  try {
    const documents=$('#use-documents').checked;
    if(historyMode!==documents){history=[];historyMode=documents;}
    const payload=providerPayload(question,documents);
    if(payload.provider!=='local'&&documents){payload.preview=await previewCloudChat(payload);if(!payload.preview){setBusy(false);return;}}
    const job=await api('/api/chat',payload);
    appendMessage('user',question);if(!documents) history.push({role:'user',content:question});
    $('#chat-input').value='';updateJob(job);
  } catch(e) {setBusy(false);toast(e.message);}
}
let librarySearchSequence=0;
async function searchLibrary() {
  const query=$('#library-query').value.trim();if(!query)return;
  const sequence=++librarySearchSequence;
  $('#library-search-status').textContent='Yerel dosyalarda aranıyor…';
  $('#library-results').innerHTML='<div class="empty-state">Yerel dosyalarda aranıyor…</div>';
  try {
    const result=await api('/api/library/search?q='+encodeURIComponent(query));
    if(sequence!==librarySearchSequence)return;
    $('#library-results').innerHTML=result.results.map((x,i)=>`<article class="result"><div class="result-actions"><h3 data-user-content>${i+1}. ${esc(x.title)}</h3><button class="launch-button" data-file="${esc(x.path)}">Dosyayı aç ↗</button></div><span class="result-path">${esc(x.path)}</span><pre>${esc(x.excerpt)}</pre></article>`).join('')||'<div class="empty-state">Eşleşme bulunamadı. Daha belirgin bir kelimeyle tekrar ara.</div>';
    $('#library-search-status').textContent=`${result.results.length} sonuç bulundu.`;
  } catch(error) {
    if(sequence!==librarySearchSequence)return;
    $('#library-search-status').textContent='Arama tamamlanamadı. Yeniden dene.';
    $('#library-results').innerHTML='<div class="empty-state">Arama tamamlanamadı. Yeniden dene.</div>';
    throw error;
  }
}
document.addEventListener('click',async event=>{
  const b=event.target.closest('button,[data-view]');if(!b||b.disabled)return;
  try {
    if(b.dataset.view)navigate(b.dataset.view);
    if(b.dataset.open)toast((await api('/api/open',{id:b.dataset.open})).message);
    if(b.dataset.favorite){const favorites=state.favorites.includes(b.dataset.favorite)?state.favorites.filter(x=>x!==b.dataset.favorite):[...state.favorites,b.dataset.favorite];state.favorites=(await api('/api/favorites',{favorites})).favorites;renderApps();}
    if(b.dataset.filter){filter=b.dataset.filter;renderApps();}
    if(b.dataset.project)toast((await api('/api/project/open',{id:b.dataset.project,editor:b.dataset.editor==='true'})).message);
    if(b.dataset.package)toast((await api('/api/package/open',{id:b.dataset.package})).message);
    if(b.dataset.file)toast((await api('/api/library/open',{path:b.dataset.file})).message);
    if(b.dataset.prompt){$('#chat-input').value=b.dataset.prompt;$('#use-documents').checked=b.dataset.documents==='true';renderChatMode();$('#chat-input').focus();}
  }catch(e){toast(e.message);}
});
$('#app-search').addEventListener('input',()=>state&&renderApps());$('#archive-query').addEventListener('input',()=>state&&renderArchive());
$('#refresh').onclick=()=>refresh().then(()=>toast('Durum yenilendi.')).catch(e=>toast(e.message));
$('#chat-form').onsubmit=e=>{e.preventDefault();submitChat();};
$('#chat-input').onkeydown=e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();submitChat();}};
$('#clear-chat').onclick=()=>api('/api/chat/clear',{}).then(()=>{history=[];activeJob=null;finishedJob=null;$('#chat-thread').replaceChildren();$('#chat-progress').hidden=true;toast('Sohbet temizlendi.');}).catch(e=>toast(e.message));
$('#stop-model').onclick=()=>api('/api/model/stop',{}).then(x=>{toast(x.message);$('#model-status').textContent='Durduruldu';}).catch(e=>toast(e.message));
$('#library-form').onsubmit=e=>{e.preventDefault();searchLibrary().catch(e=>toast(e.message));};
$('#index-library').onclick=()=>api('/api/library/index',{}).then(x=>toast(x.message)).catch(e=>toast(e.message));
$('#ask-library').onclick=()=>{const q=$('#library-query').value.trim();if(!q){toast('Önce bir soru veya konu yaz.');return;}$('#chat-input').value=q;$('#use-documents').checked=true;renderChatMode();navigate('chat');$('#chat-input').focus();};
$('#backup-start').onclick=()=>api('/api/backup',{}).then(x=>toast(x.message)).catch(e=>toast(e.message));
$('#shutdown').onclick=()=>api('/api/shutdown',{}).then(x=>{document.body.classList.add('closed');toast(x.message);}).catch(e=>toast(e.message));
window.addEventListener('hashchange',()=>navigate(location.hash.slice(1)));
document.addEventListener('keydown',e=>{if(e.key==='/'&&!document.querySelector('dialog[open]')&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)){e.preventDefault();navigate('apps');$('#app-search').focus();}});
setInterval(async()=>{
  if(document.body.classList.contains('closed'))return;
  try{if(activeJob&&['loading','generating'].includes(activeJob.status)){const x=await api('/api/job');if(x.job)updateJob(x.job);}if(view==='library')renderLibraryStatus(await api('/api/library/status'));}catch(e){$('#chat-progress').textContent='Yerel bağlantı kesildi. FieldDesk’i yeniden açabilirsin.';setBusy(false);}
},2000);
navigate(location.hash.slice(1));refresh().then(()=>{if(!state.setup.completed&&view==='home')navigate('setup');}).catch(e=>toast('Çanta okunamadı: '+e.message));

function renderChatMode(){
  const documents=$('#use-documents').checked;
  $('#chat-mode-title').textContent=documents?'Belgelerle sohbet':'Normal sohbet';
  $('#chat-mode-help').textContent=documents?'Belge modu · İlgili yerel alıntılar kullanılır.':'Normal sohbet · Belgeler aranmaz.';
  if(typeof renderProviders==='function'&&state)renderProviders();
}
$('#use-documents').addEventListener('change',renderChatMode);
document.addEventListener('fielddesk-language',event=>{
  if(event.detail?.persist)api('/api/preferences',{language:event.detail.language}).then(x=>{if(state)state.preferences=x;}).catch(e=>toast(e.message));
  if(!state)return;
  renderApps();renderProjects();renderArchive();renderLibraryStatus(state.library);
  $('#stat-files').textContent=num(state.library.files);
  $('#stat-disk').textContent=(state.device.free_disk_gb/1000).toLocaleString(uiLocale(),{minimumFractionDigits:2,maximumFractionDigits:2})+' TB';
});
renderChatMode();
