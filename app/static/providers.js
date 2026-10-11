'use strict';
let connectionBusy=false, pendingCloudPreview=null;
function selectedProvider(){return $('#provider-select').value||'local';}
function providerRow(){return state?.connections?.providers.find(x=>x.id===selectedProvider());}
function providerPayload(question,documents){return {question,documents,provider:selectedProvider(),model:selectedProvider()==='local'?$('#model-select').value:$('#cloud-model').value.trim(),history:documents?[]:history.slice(-6)};}
function renderProviders(reset=false){
  const select=$('#provider-select'), previous=select.value||'local';
  if(select.options.length===1){select.innerHTML='<option value="local">Bu bilgisayar · Çevrimdışı</option>'+state.connections.providers.map(x=>`<option value="${esc(x.id)}">${esc(x.name)}</option>`).join('');select.value=previous;}
  const cloud=previous!=='local', row=providerRow();
  $('#local-model-fields').hidden=cloud;$('#cloud-model-fields').hidden=!cloud;
  $('#provider-notice').classList.toggle('cloud',cloud);
  if(!cloud){$('#provider-notice').textContent=$('#use-documents').checked?'Yerel mod · Mesajlar ve belge alıntıları bu bilgisayarda işlenir.':'Yerel mod · Mesajlar bu bilgisayarda işlenir.';return;}
  $('#provider-notice').textContent=`${row.name} · Gönderdiğin mesaj ve bu sağlayıcıyla yakın sohbet geçmişi ${row.base||'kaydettiğin API adresine'} gönderilir. Belge alıntıları ayrıca önizlenir. Ücret ve kota hesabına aittir.`;
  $('#custom-api-fields').hidden=row.id!=='custom';
  $('#provider-settings-title').textContent=row.name;
  if(!activeJob)$('#model-status').textContent='API bağlantısı seçildi';
  if(reset||!$('#cloud-model').dataset.initialized){$('#cloud-model').value=row.model;$('#cloud-model').dataset.initialized='true';$('#provider-base').value=row.base;$('#provider-protocol').value=row.protocol;$('#provider-key').value='';$('#provider-remember').checked=row.remember;$('#provider-models').replaceChildren();}
  $('#provider-key').placeholder=row.configured?'Yeni anahtar veya boş bırakarak mevcut anahtar':'Anahtarını buraya gir';
  $('#provider-config-status').textContent=state.connections.warning||(row.configured?(row.remember?'Windows hesabına bağlı şifreli kayıt.':'Oturumluk bağlantı kaydedildi.')+' Canlı erişim için bağlantıyı dene.':'Henüz bağlantı kaydedilmedi.');
  $('#provider-key-link').hidden=!row.key_url;$('#provider-key-link').href=row.key_url||'#';
  for(const id of ['provider-list','provider-test','provider-forget'])$('#'+id).disabled=!row.configured||connectionBusy;
}
function providerBusy(busy){connectionBusy=busy;for(const node of document.querySelectorAll('#provider-form input,#provider-form select,#provider-form button,#provider-select,#cloud-model,.provider-actions button'))node.disabled=busy;}
document.addEventListener('atolye-state',()=>renderProviders());
$('#provider-select').onchange=async()=>{
  try{await api('/api/chat/clear',{});history=[];activeJob=null;finishedJob=null;$('#chat-thread').replaceChildren();$('#chat-progress').hidden=true;renderProviders(true);$('#model-status').textContent=selectedProvider()==='local'?'Gerektiğinde başlar':'API bağlantısı seçildi';}
  catch(e){$('#provider-select').value=activeJob?.provider||'local';toast(e.message);}
};
$('#provider-form').onsubmit=async e=>{
  e.preventDefault();if(connectionBusy)return;providerBusy(true);
  try{const result=await api('/api/providers/save',{provider:selectedProvider(),key:$('#provider-key').value,base:$('#provider-base').value,protocol:$('#provider-protocol').value,model:$('#cloud-model').value.trim(),remember:$('#provider-remember').checked});$('#provider-key').value='';history=[];activeJob=null;finishedJob=null;$('#chat-thread').replaceChildren();$('#chat-progress').hidden=true;await refresh();renderProviders(true);$('#provider-settings-dialog').close();toast(result.message);}
  catch(e){$('#provider-save-status').textContent=e.message;toast(e.message);}finally{providerBusy(false);renderProviders();}
};
$('#open-provider-settings').onclick=()=>{$('#provider-save-status').textContent='';$('#provider-settings-dialog').showModal();};
$('#provider-settings-close').onclick=()=>{$('#provider-key').value='';$('#provider-settings-dialog').close();};
$('#provider-settings-dialog').addEventListener('cancel',()=>{$('#provider-key').value='';});
$('#cloud-model').onchange=async()=>{if(!providerRow()?.configured||!$('#cloud-model').value.trim())return;try{const result=await api('/api/providers/model',{provider:selectedProvider(),model:$('#cloud-model').value.trim()});state.connections={providers:result.providers,warning:result.warning};}catch(e){toast(e.message);}};
async function connectionAction(action){
  if(connectionBusy)return;providerBusy(true);$('#provider-config-status').textContent='Servis yanıtı bekleniyor…';
  try{const result=await api('/api/providers/'+action,{provider:selectedProvider(),model:$('#cloud-model').value.trim()});
    if(action==='models'){$('#provider-models').innerHTML=result.models.map(x=>`<option value="${esc(x)}"></option>`).join('');toast(result.models.length+' model. '+result.message);}
    else if(action==='forget'){history=[];activeJob=null;finishedJob=null;$('#chat-thread').replaceChildren();$('#chat-progress').hidden=true;await refresh();renderProviders(true);$('#provider-settings-dialog').close();toast(result.message);}
    else {toast(result.message);}
    $('#provider-config-status').textContent=result.message;
  }catch(e){$('#provider-config-status').textContent=e.message;toast(e.message);}finally{providerBusy(false);}
}
$('#provider-list').onclick=()=>connectionAction('models');$('#provider-test').onclick=()=>connectionAction('test');$('#provider-forget').onclick=()=>connectionAction('forget');
async function previewCloudChat(payload){
  const result=await api('/api/chat/preview',payload);
  $('#cloud-preview-destination').textContent='Hedef: '+result.destination+' · Model: '+payload.model;
  $('#cloud-preview-description').textContent=result.message;
  $('#cloud-preview-question').textContent=result.question;
  $('#cloud-preview-sources').innerHTML=result.sources.map((x,i)=>`<article class="cloud-preview-source"><small>[${i+1}] ${esc(x.title)} · ${esc(x.path)} (ad ve yol gönderilmez)</small><pre>${esc(x.excerpt)}</pre></article>`).join('');
  return new Promise(resolve=>{pendingCloudPreview={resolve,id:result.id};$('#cloud-preview-dialog').showModal();});
}
function resolveCloudPreview(approved){if(pendingCloudPreview){const pending=pendingCloudPreview;pendingCloudPreview=null;pending.resolve(approved?pending.id:null);}$('#cloud-preview-dialog').close();}
$('#cloud-preview-confirm').onclick=()=>resolveCloudPreview(true);$('#cloud-preview-close').onclick=()=>resolveCloudPreview(false);$('#cloud-preview-cancel').onclick=()=>resolveCloudPreview(false);
$('#cloud-preview-dialog').addEventListener('cancel',e=>{e.preventDefault();resolveCloudPreview(false);});
