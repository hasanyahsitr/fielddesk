'use strict';
let workflowKind='pdf', workflowFiles=[], workflowPlan=null, workflowJob=null, workflowUploading=false;
let pickerKind='apps', pickerPath='', pickerParent=null, pickerSelected=new Map(), setupPlan=null;
function invalidatePlan(){workflowPlan=null;$('#workflow-run').hidden=true;$('#workflow-plan').innerHTML='<div class="preview-empty"><span>⇄</span><h3>İşlem önizlemesi</h3><p>Dosyalarını seç ve sonucu önizle.</p></div>';}
function workflowBusy(){return workflowUploading||workflowJob?.status==='running';}
function renderWorkflowFiles(){
  $('#workflow-files').innerHTML=workflowFiles.map((x,i)=>`<div class="file-row"><span class="file-number">${i+1}</span><div><strong>${esc(x.name)}</strong><small>${x.bytes?num(Math.ceil(x.bytes/1024))+' KB':esc(x.path)}</small></div><button data-move-file="${i}" data-direction="-1" aria-label="Yukarı taşı: ${esc(x.name)}" ${i===0?'disabled':''}>↑</button><button data-move-file="${i}" data-direction="1" aria-label="Aşağı taşı: ${esc(x.name)}" ${i===workflowFiles.length-1?'disabled':''}>↓</button><button data-remove-file="${i}" aria-label="Kaldır: ${esc(x.name)}">×</button></div>`).join('')||'<div class="empty-state">Henüz dosya seçilmedi.</div>';
}
function setWorkflow(kind){
  if(workflowBusy()){toast('Önce devam eden işlemin tamamlanmasını bekle.');return;}
  workflowKind=kind;workflowFiles=[];invalidatePlan();renderWorkflowFiles();
  document.querySelectorAll('[data-workflow]').forEach(x=>{x.classList.toggle('selected',x.dataset.workflow===kind);x.setAttribute('aria-pressed',x.dataset.workflow===kind);});
  $('#workflow-heading').textContent={pdf:'Belgeleri seç',images:'Görselleri seç',project:'Çalışma alanı seç',ocr:'Okunacak belgeleri seç'}[kind];
  $('#workflow-files-area').hidden=kind==='project';$('#image-options').hidden=kind!=='images';$('#project-options').hidden=kind!=='project';
  $('#workflow-upload').accept=kind==='pdf'?'.pdf':kind==='ocr'?'.pdf,.png,.jpg,.jpeg,.webp':'.png,.jpg,.jpeg,.webp';$('#ocr-options').hidden=kind!=='ocr';$('#ocr-note').hidden=kind!=='ocr';
  $('#workflow-message').textContent='';$('#workflow-progress').hidden=true;$('#workflow-open-output').hidden=true;$('#workflow-cancel').hidden=true;$('#workflow-index').hidden=true;
}
function renderPlan(plan){
  workflowPlan=plan;
  let rows=plan.files.map((x,i)=>`<div class="plan-row"><b>${i+1}</b><span>${esc(x.name)}</span><small>${(plan.kind==='pdf'||plan.kind==='ocr')?x.pages+' sayfa':`${x.width}×${x.height} → ${x.output_width}×${x.output_height}`}</small></div>`).join('');
  if(plan.kind==='project')rows=`<div class="plan-note"><strong>${esc(plan.project.path)}</strong><p>${plan.tools.length} taşınabilir araç yolu bulundu.</p><p>node_modules: ${plan.node_modules?'var':'bulunamadı'} · npm komutları: ${esc(plan.scripts.join(', ')||'yok')}</p></div>`;
  $('#workflow-plan').innerHTML=`<h2>${esc(plan.title)}</h2><p class="plan-summary">${esc(plan.summary)}</p>${rows}<div class="plan-warnings">${plan.warnings.map(x=>`<p>ⓘ ${esc(x)}</p>`).join('')}<p>Çıktılar ayrı bir klasöre yazılır. Kaynak dosyalar değişmez.</p></div>`;
  $('#workflow-run').hidden=false;$('#workflow-run').disabled=false;
}
function updateWorkflowJob(job){
  workflowJob=job;if(!job)return;
  const busy=job.status==='running';$('#workflow-cancel').hidden=!(busy&&job.kind==='ocr');$('#workflow-index').hidden=!(job.status==='complete'&&job.kind==='ocr');$('#workflow-progress').hidden=false;$('#workflow-progress').classList.toggle('busy',busy);
  for(const id of ['ocr-language','ocr-rotation','image-width','image-format','image-quality','workflow-project','workflow-editor'])$('#'+id).disabled=busy;
  $('#workflow-progress').textContent=job.message+(busy?` (${job.done}/${job.total})`:'');
  $('#workflow-run').hidden=true;$('#workflow-preview').disabled=busy||workflowUploading;
  $('#workflow-open-output').hidden=!job.output;
  $('#workflow-upload').disabled=busy;$('#workflow-browse').disabled=busy;
  if(job.status==='complete'){
    $('#workflow-plan').innerHTML=`<div class="step-label">TAMAMLANDI ✓</div><h2>${esc(job.title)}</h2><p class="plan-summary">${esc(job.message)}</p>${job.results.map(x=>`<div class="plan-row"><span>${esc(x.name)}</span><small>${num(Math.ceil(x.bytes/1024))} KB${x.pages?' · '+x.pages+' sayfa':x.width?' · '+x.width+'×'+x.height:''}</small></div>`).join('')}<p class="fine-print">${esc(job.output)}<br>Doğrulama ve işlem ayrıntıları islem-raporu.json dosyasında.</p>${job.text_preview?`<h3 class="ocr-preview-heading">Okunan metin</h3><pre class="ocr-text">${esc(job.text_preview)}</pre><p class="fine-print">${(job.warnings||[]).map(esc).join('<br>')}</p>`:''}`;
  }
  if(['cancelled','error'].includes(job.status))$('#workflow-plan').innerHTML=`<div class="step-label">${job.status==='cancelled'?'İPTAL EDİLDİ':'TAMAMLANAMADI'}</div><h2>${esc(job.title)}</h2><p class="plan-summary">${esc(job.message)}</p><p class="fine-print">Bu işlem başarılı sonuç olarak kaydedilmedi. Kaynak dosyalar korundu.</p>`;
}
async function openPicker(kind){pickerKind=kind;pickerSelected=new Map();$('#picker-dialog').showModal();await loadPicker(kind==='apps'?'01_TASINABILIR':'');}
async function loadPicker(path){
  const x=await api('/api/browse?path='+encodeURIComponent(path)+'&kind='+pickerKind);pickerPath=x.path;pickerParent=x.parent;
  $('#picker-path').textContent=x.path||'Çanta kökü';$('#picker-up').disabled=x.parent===null;
  $('#picker-list').innerHTML=x.entries.map(x=>x.directory?`<button class="picker-row" data-directory="${esc(x.path)}"><span>▥</span><strong>${esc(x.name)}</strong><small>→</small></button>`:`<button class="picker-row ${pickerSelected.has(x.path)?'selected':''}" data-pick-file="${esc(x.path)}" data-filename="${esc(x.name)}" data-bytes="${x.bytes}" aria-pressed="${pickerSelected.has(x.path)}"><span>${pickerSelected.has(x.path)?'✓':'□'}</span><strong>${esc(x.name)}</strong><small>${num(Math.ceil(x.bytes/1024))} KB</small></button>`).join('')||'<div class="empty-state">Bu klasörde uygun dosya bulunamadı.</div>';
}
document.addEventListener('atolye-state',()=>{
  const current=$('#workflow-project').value;
  $('#workflow-project').innerHTML=state.projects.map(x=>`<option value="${esc(x.id)}">${esc(x.name)} · ${esc(x.kind)}</option>`).join('');if(current)$('#workflow-project').value=current;
  $('#setup-root').value=state.root;$('#setup-badge').textContent=state.setup.completed?'HAZIRLIK TAMAMLANDI':'İLK AÇILIŞ';
  if(state.workflow){
    if(!workflowJob){setWorkflow(state.workflow.kind);updateWorkflowJob(state.workflow);}
    else if(state.workflow.id!==workflowJob.id||state.workflow.status==='running')updateWorkflowJob(state.workflow);
  }
});
document.addEventListener('click',async e=>{
  const b=e.target.closest('button');if(!b||b.disabled)return;
  try{
    if(b.dataset.close)$('#'+b.dataset.close).close();
    if(b.dataset.workflow)setWorkflow(b.dataset.workflow);
    if(b.dataset.moveFile!==undefined){if(workflowBusy())return;const i=Number(b.dataset.moveFile),j=i+Number(b.dataset.direction);[workflowFiles[i],workflowFiles[j]]=[workflowFiles[j],workflowFiles[i]];renderWorkflowFiles();invalidatePlan();}
    if(b.dataset.removeFile!==undefined){if(workflowBusy())return;workflowFiles.splice(Number(b.dataset.removeFile),1);renderWorkflowFiles();invalidatePlan();}
    if(b.dataset.directory!==undefined)await loadPicker(b.dataset.directory);
    if(b.dataset.pickFile){
      if(pickerKind==='apps'){$('#custom-path').value=b.dataset.pickFile;$('#picker-dialog').close();if(!$('#custom-name').value)$('#custom-name').value=b.dataset.filename.replace(/\.exe$/i,'');}
      else {if(pickerSelected.has(b.dataset.pickFile))pickerSelected.delete(b.dataset.pickFile);else pickerSelected.set(b.dataset.pickFile,{path:b.dataset.pickFile,name:b.dataset.filename,bytes:Number(b.dataset.bytes)});await loadPicker(pickerPath);}
    }
    if(b.dataset.removeApp){toast((await api('/api/apps/remove',{id:b.dataset.removeApp})).message);await refresh();}
  }catch(error){toast(error.message);}
});
$('#add-app').onclick=()=>{$('#add-app-form').reset();$('#custom-message').textContent='';$('#app-dialog').showModal();};
$('#custom-browse').onclick=()=>openPicker('apps').catch(e=>toast(e.message));
$('#add-app-form').onsubmit=async e=>{e.preventDefault();try{const x=await api('/api/apps/add',{name:$('#custom-name').value,relative:$('#custom-path').value,description:$('#custom-description').value,category:$('#custom-category').value});$('#app-dialog').close();await refresh();toast(x.message);}catch(error){$('#custom-message').textContent=error.message;}};
$('#picker-up').onclick=()=>loadPicker(pickerParent||'').catch(e=>toast(e.message));
$('#picker-done').onclick=()=>{if(pickerKind!=='apps'){for(const x of pickerSelected.values())if(!workflowFiles.some(f=>f.path===x.path))workflowFiles.push(x);renderWorkflowFiles();invalidatePlan();}$('#picker-dialog').close();};
$('#workflow-browse').onclick=()=>openPicker(workflowKind).catch(e=>toast(e.message));
$('#workflow-upload').onchange=async e=>{
  const files=[...e.target.files];if(!files.length)return;
  if(workflowBusy()){toast('Önce devam eden işlemi bekle.');return;}
  if(files.length+workflowFiles.length>30||files.some(x=>x.size>50*1024*1024)||files.reduce((n,x)=>n+x.size,0)>150*1024*1024){toast('En fazla 30 dosya; dosya başına 50 MB, toplam 150 MB seç.');e.target.value='';return;}
  workflowUploading=true;$('#workflow-preview').disabled=true;invalidatePlan();
  try{
    for(let i=0;i<files.length;i++){
      $('#workflow-message').textContent=`${i+1}/${files.length} dosya çantaya kopyalanıyor…`;
      const response=await fetch('/api/workflows/upload',{method:'POST',headers:{'X-Atolye-Token':token,'X-Atolye-Filename':encodeURIComponent(files[i].name),'Content-Type':'application/octet-stream'},body:files[i]});
      const x=await response.json();if(!response.ok)throw Error(x.message);workflowFiles.push(x);renderWorkflowFiles();
    }
    $('#workflow-message').textContent='Dosyalar eklendi. Önizlemeye geçebilirsin.';
  }catch(error){$('#workflow-message').textContent=error.message;}finally{workflowUploading=false;$('#workflow-preview').disabled=false;e.target.value='';}
};
for(const id of ['image-width','image-format','image-quality','workflow-project','workflow-editor','ocr-language','ocr-rotation'])$('#'+id).addEventListener('change',invalidatePlan);
$('#workflow-preview').onclick=async()=>{
  if(workflowBusy())return;$('#workflow-preview').disabled=true;$('#workflow-message').textContent='Girdiler okunuyor ve kontrol ediliyor…';$('#workflow-open-output').hidden=true;
  try{const plan=await api('/api/workflows/preview',{kind:workflowKind,files:workflowFiles.map(x=>x.path),options:{width:Number($('#image-width').value),quality:Number($('#image-quality').value),format:$('#image-format').value,language:$('#ocr-language').value,rotation:Number($('#ocr-rotation').value)},project:$('#workflow-project').value,editor:$('#workflow-editor').checked});renderPlan(plan);$('#workflow-message').textContent='Önizleme hazır. Onayladığında işlem başlar.';}catch(error){invalidatePlan();$('#workflow-message').textContent=error.message;}finally{$('#workflow-preview').disabled=false;}
};
$('#workflow-run').onclick=async()=>{if(!workflowPlan)return;$('#workflow-run').disabled=true;try{const x=await api('/api/workflows/run',{preview:workflowPlan.id});workflowPlan=null;updateWorkflowJob(x);}catch(error){toast(error.message);$('#workflow-run').disabled=false;}};
$('#workflow-cancel').onclick=()=>api('/api/workflows/cancel',{}).then(x=>toast(x.message)).catch(e=>toast(e.message));
$('#workflow-index').onclick=()=>api('/api/library/index',{}).then(x=>toast(x.message+' Bilgi merkezinden arayabilirsin.')).catch(e=>toast(e.message));
$('#workflow-open-output').onclick=()=>workflowJob&&api('/api/workflows/open',{id:workflowJob.id}).then(x=>toast(x.message)).catch(e=>toast(e.message));
$('#setup-check').onclick=async()=>{try{setupPlan=await api('/api/setup/preview',{root:$('#setup-root').value});$('#setup-results').innerHTML=`<div class="system-grid"><article class="system-card"><span class="eyebrow">PDF İŞ AKIŞI</span><h3>${setupPlan.dependencies.pdf.ready?'Hazır ✓':'Paket eksik'}</h3><p>pypdf</p></article><article class="system-card"><span class="eyebrow">GÖRSEL İŞ AKIŞI</span><h3>${setupPlan.dependencies.images.ready?'Hazır ✓':'Paket eksik'}</h3><p>Pillow</p></article><article class="system-card"><span class="eyebrow">METİN OKUMA · OCR</span><h3>${setupPlan.dependencies.ocr.ready?'Hazır ✓':'Motor eksik'}</h3><p>${esc(setupPlan.dependencies.ocr.languages.join(', ')||setupPlan.dependencies.ocr.message)}</p></article><article class="system-card"><span class="eyebrow">ÇALIŞMA ALANI</span><h3>${setupPlan.writable?'Yazılabilir ✓':'Yazma izni yok'}</h3><p>${esc(setupPlan.root)}</p></article></div><article class="result"><h3>Taşınabilir araçlar</h3>${setupPlan.tools.map(x=>`<div class="setup-folder"><span>${esc(x.name)}</span><small>${x.ready?'Hazır ✓':'Eklenmemiş'}</small></div>`).join('')}<p class="fine-print">Bu araçlar ilgili uygulama, proje veya asistan özelliği için kullanılır. PDF ve görsel işlemleri yukarıdaki paketlerle çalışır.</p></article><article class="result"><h3>Çanta klasörleri</h3>${setupPlan.folders.map(x=>`<div class="setup-folder"><span>${esc(x.path)}</span><small>${x.exists?'Var ✓':'Oluşturulacak +'}</small></div>`).join('')}<p class="fine-print">${esc(setupPlan.message)}</p></article>`;$('#setup-apply').hidden=false;$('#setup-apply').disabled=!setupPlan.writable;$('#setup-message').textContent='Kontrol tamamlandı.';}catch(error){$('#setup-message').textContent=error.message;$('#setup-apply').hidden=true;}};
$('#setup-root').oninput=()=>{setupPlan=null;$('#setup-apply').hidden=true;};
$('#setup-apply').onclick=async()=>{if(!setupPlan)return;try{const x=await api('/api/setup/apply',{root:setupPlan.root});await refresh();toast(x.message);navigate('home');}catch(error){$('#setup-message').textContent=error.message;}};
$('#setup-folder').onclick=async()=>{try{const x=await api('/api/setup/folder',{});if(x.path){$('#setup-root').value=x.path;setupPlan=null;$('#setup-apply').hidden=true;}}catch(error){toast(error.message);}};
setInterval(async()=>{if(workflowJob?.status==='running'&&!document.body.classList.contains('closed'))try{const x=await api('/api/workflows/job');if(x.job)updateWorkflowJob(x.job);}catch(e){$('#workflow-progress').textContent='Yerel bağlantı kesildi. İşlem durumunu yeniden açarak kontrol et.';}},1000);
if(state)document.dispatchEvent(new CustomEvent('atolye-state'));
