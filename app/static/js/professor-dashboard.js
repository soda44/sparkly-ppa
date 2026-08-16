  const LETRAS = ['A','B','C','D','E','F','G','H'];
  let questoesCache = [];

  const profSS = JSON.parse(sessionStorage.getItem('professor')||'null');
  if (!profSS) {
    fetch('/api/professor/turmas').then(r=>{if(r.status===401)window.location.href='/login';}).catch(()=>window.location.href='/login');
  } else {
    const nome = profSS.nome||profSS.nome_completo||'Professor';
    document.getElementById('professorNome').textContent = nome;
    document.getElementById('professorAvatar').textContent = nome.charAt(0).toUpperCase();
  }

  function showSection(id) {
    document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
    document.getElementById('sec-'+id).classList.add('active');
    document.getElementById('nav-'+id).classList.add('active');
    if(id==='turmas')  carregarTurmas();
    if(id==='questoes') carregarQuestoes();
  }

  function toast(msg, tipo='success') {
    const t = document.getElementById('toast');
    t.textContent = msg; t.className = 'show '+tipo;
    setTimeout(()=>{t.className='';},3500);
  }

  async function carregarTurmas() {
    const grid = document.getElementById('turmasGrid');
    grid.innerHTML = '<div class="loading"><div class="spinner" style="margin:0 auto 10px;"></div>Carregando...</div>';
    try {
      const r = await fetch('/api/professor/turmas');
      if(r.status===401){window.location.href='/login';return;}
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      renderTurmas(data.turmas);
    } catch(e) {
      grid.innerHTML=`<div class="empty-state"><div class="em-icon"></div><div class="em-text">Erro: ${e.message}</div></div>`;
    }
  }

  function renderTurmas(turmas) {
    const grid = document.getElementById('turmasGrid');
    document.getElementById('stat-turmas').textContent = turmas.length;
    document.getElementById('stat-licoes').textContent = turmas.reduce((s,t)=>s+t.total_licoes,0);
    document.getElementById('stat-alunos').textContent = turmas.reduce((s,t)=>s+t.total_alunos,0);
    if(!turmas.length){
      grid.innerHTML=`<div class="empty-state" style="grid-column:1/-1"><div class="em-icon">📭</div><div class="em-text">Nenhuma turma encontrada.</div></div>`;
      return;
    }
    grid.innerHTML = turmas.map(t=>`
      <div class="turma-card" onclick="verTurma(${t.id})">
        <div class="t-header">
          <div class="t-nome">${t.nome}</div>
          <div class="t-sala">Sala ${t.numero_sala||'—'}</div>
        </div>
        <div class="t-stats">
          <div class="t-stat"><div class="ts-num">${t.total_licoes}</div><div class="ts-label">Lições</div></div>
          <div class="t-stat"><div class="ts-num">${t.total_alunos}</div><div class="ts-label">Alunos</div></div>
        </div>
        <button class="btn btn-outline btn-sm btn-full mt-2">Ver turma →</button>
      </div>`).join('');
  }

  async function verTurma(id) {
    document.getElementById('turmasGrid').style.display='none';
    document.getElementById('statsRow').style.display='none';
    document.querySelectorAll('#sec-turmas .page-title, #sec-turmas .page-sub').forEach(el=>el.style.display='none');
    const det = document.getElementById('turmaDetalhe');
    det.innerHTML='<div class="loading"><div class="spinner" style="margin:0 auto 10px;"></div>Carregando detalhes...</div>';
    det.style.display='block';
    try {
      const r = await fetch(`/api/professor/turmas/${id}`);
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      renderDetalhe(data);
    } catch(e) {
      det.innerHTML=`<button class="back-btn" onclick="fecharDetalhe()">← Voltar</button>
        <div class="empty-state"><div class="em-icon"></div><div class="em-text">${e.message}</div></div>`;
    }
  }

  function renderDetalhe(data) {
    const det = document.getElementById('turmaDetalhe');
    const {turma,licoes,alunos} = data;
    const badgeClass = tipo => ({'aula':'badge-blue','exercicio':'badge-yellow','prova':'badge-red'}[(tipo||'').toLowerCase()]||'badge-neutral');
    const notaClass  = v => v>=7?'nota-alta':v>=5?'nota-media':'nota-baixa';
    det.innerHTML = `
      <button class="back-btn" onclick="fecharDetalhe()">← Voltar às turmas</button>
      <div class="page-title mb-1">${turma.nome}</div>
      <div class="page-sub mb-3">Sala ${turma.numero_sala||'—'} · ID ${turma.id}</div>
      <div class="detalhe-grid">
        <div class="panel">
          <div class="panel-title"><span> Lições</span><span class="badge badge-blue">${licoes.length}</span></div>
          ${licoes.length===0
            ? '<div class="empty-state" style="padding:20px"><div class="em-icon"></div><div class="em-text">Nenhuma lição cadastrada</div></div>'
            : `<table class="table">
                <thead><tr><th>Tipo</th><th>Descrição</th><th>Nota</th></tr></thead>
                <tbody>${licoes.map(l=>`
                  <tr>
                    <td><span class="badge ${badgeClass(l.tipo)}">${l.tipo}</span></td>
                    <td>${l.descricao||'—'}</td>
                    <td style="color:var(--yellow-dk);font-weight:800;">${l.nota!=null?l.nota:'—'}</td>
                  </tr>`).join('')}
                </tbody></table>`}
        </div>
        <div class="panel">
          <div class="panel-title"><span>👥 Alunos</span><span class="badge badge-green">${alunos.length}</span></div>
          ${alunos.length===0
            ? '<div class="empty-state" style="padding:20px"><div class="em-icon">👥</div><div class="em-text">Nenhum aluno nesta turma</div></div>'
            : `<table class="table">
                <thead><tr><th>Nome</th><th>Usuário</th><th>Média</th></tr></thead>
                <tbody>${alunos.map(a=>`
                  <tr>
                    <td>${a.nome}</td>
                    <td class="text-muted">@${a.usuario}</td>
                    <td class="${notaClass(a.media)}">${a.media}</td>
                  </tr>`).join('')}
                </tbody></table>`}
        </div>
      </div>`;
  }

  function fecharDetalhe() {
    document.getElementById('turmaDetalhe').style.display='none';
    document.getElementById('turmasGrid').style.display='grid';
    document.getElementById('statsRow').style.display='grid';
    document.querySelectorAll('#sec-turmas .page-title, #sec-turmas .page-sub').forEach(el=>el.style.display='');
    carregarTurmas();
  }

  async function carregarQuestoes() {
    const list = document.getElementById('questoesList');
    list.innerHTML='<div class="loading"><div class="spinner" style="margin:0 auto 10px;"></div>Carregando...</div>';
    try {
      const r = await fetch('/api/professor/questoes');
      if(r.status===401){window.location.href='/login';return;}
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      questoesCache = data.questoes;
      renderQuestoes(data.questoes);
    } catch(e) {
      list.innerHTML=`<div class="empty-state"><div class="em-icon"></div><div class="em-text">${e.message}</div></div>`;
    }
  }

  const TIPO_LABEL = {'multipla-escolha':'Múltipla Escolha','multi-selecao':'Múltipla Seleção','entrada-texto':'Dissertativa'};

  function renderQuestoes(questoes) {
    const list = document.getElementById('questoesList');
    if(!questoes.length){
      list.innerHTML=`<div class="empty-state"><div class="em-icon"></div><div class="em-text">Nenhuma questão. Crie a primeira!</div></div>`;
      return;
    }
    list.innerHTML = questoes.map(q=>`
      <div class="questao-item">
        <div class="questao-info">
          <div class="q-nome">${q.nome}</div>
          <div class="q-tipo">${TIPO_LABEL[q.tipo]||q.tipo}</div>
        </div>
        <div class="questao-actions">
          <button class="btn-icon info" onclick="verQuestao(${q.id})" title="Ver">👁</button>
          <button class="btn-icon edit" onclick="editarQuestao(${q.id})" title="Editar">✏️</button>
          <button class="btn-icon danger" onclick="deletarQuestao(${q.id},'${q.nome.replace(/'/g,"\\'")}')">🗑</button>
        </div>
      </div>`).join('');
  }

  function verQuestao(id) {
    const q = questoesCache.find(x=>x.id===id); if(!q) return;
    document.getElementById('verQ-nome').textContent = q.nome;
    document.getElementById('verQ-tipo').textContent = TIPO_LABEL[q.tipo]||q.tipo;
    const c = q.conteudo||{};
    let html = `<div style="font-weight:700;margin-bottom:10px;">${c.enunciado||c.texto_base||'—'}</div>`;
    if(c.alternativas?.length) {
      html += c.alternativas.map((alt,i)=>
        `<div class="alt ${i===c.gabarito?'correta':''}">${LETRAS[i]}) ${alt} ${i===c.gabarito?'✓':''}</div>`).join('');
    } else if(c.gabarito!==undefined&&c.gabarito!==null&&c.gabarito!=='') {
      html+=`<div style="margin-top:10px;font-weight:700;">Gabarito: ${c.gabarito}</div>`;
    }
    document.getElementById('verQ-conteudo').innerHTML = html;
    document.getElementById('modalVerQuestao').classList.add('active');
  }
  function fecharVerQuestao() { document.getElementById('modalVerQuestao').classList.remove('active'); }

  async function deletarQuestao(id, nome) {
    if(!confirm(`Excluir "${nome}"?`)) return;
    try {
      const r = await fetch(`/api/professor/questoes/${id}`,{method:'DELETE'});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      toast('Questão excluída! ✓'); carregarQuestoes();
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  function abrirModalNovaQuestao() {
    document.getElementById('q-nome').value='';
    document.getElementById('q-enunciado').value='';
    document.getElementById('q-gabarito').value='';
    document.getElementById('q-tipo').value='multipla-escolha';
    resetAlternativas(); tipoChanged();
    document.getElementById('modalQuestao').classList.add('active');
  }
  function fecharModal() { document.getElementById('modalQuestao').classList.remove('active'); }

  function tipoChanged() {
    const tipo = document.getElementById('q-tipo').value;
    document.getElementById('bloco-alternativas').style.display = tipo==='entrada-texto'?'none':'block';
    document.getElementById('bloco-gabarito').style.display    = tipo==='entrada-texto'?'block':'none';
    if(tipo!=='entrada-texto') resetAlternativas();
  }

  function resetAlternativas() {
    const c = document.getElementById('alternativas-container');
    c.innerHTML = ['A','B','C','D'].map((l,i)=>`
      <div class="alternativa-row">
        <input type="radio" name="gabarito" value="${i}">
        <label>${l}</label>
        <input type="text" placeholder="Texto da alternativa ${l}">
      </div>`).join('');
  }

  function adicionarAlternativa() {
    const c = document.getElementById('alternativas-container');
    const idx = c.children.length; if(idx>=8){toast('Máximo 8 alternativas','error');return;}
    const l = LETRAS[idx];
    const div = document.createElement('div'); div.className='alternativa-row';
    div.innerHTML=`<input type="radio" name="gabarito" value="${idx}"> <label>${l}</label><input type="text" placeholder="Alternativa ${l}">`;
    c.appendChild(div);
  }

  async function salvarQuestao() {
    const nome = document.getElementById('q-nome').value.trim();
    const tipo = document.getElementById('q-tipo').value;
    const enunciado = document.getElementById('q-enunciado').value.trim();
    if(!nome){toast('Informe o nome','error');return;}
    if(!enunciado){toast('Informe o enunciado','error');return;}
    let conteudo = {enunciado};
    if(tipo!=='entrada-texto') {
      const rows = document.querySelectorAll('#alternativas-container .alternativa-row');
      const alternativas=[]; let gabarito=null;
      rows.forEach((row,i)=>{
        const radio=row.querySelector('input[type=radio]');
        const txt=row.querySelector('input[type=text]').value.trim();
        alternativas.push(txt||`Alternativa ${LETRAS[i]}`);
        if(radio?.checked) gabarito=i;
      });
      if(gabarito===null){toast('Marque a alternativa correta','error');return;}
      conteudo.alternativas=alternativas; conteudo.gabarito=gabarito;
    } else {
      conteudo.gabarito=document.getElementById('q-gabarito').value.trim();
    }
    try {
      const r = await fetch('/api/professor/questoes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome,tipo,conteudo})});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro||JSON.stringify(data));
      toast('Questão criada! ✓'); fecharModal(); carregarQuestoes();
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  async function sincronizarInstancias() {
    try {
      const r = await fetch('/api/professor/sincronizar-instancias',{method:'POST'});
      const data = await r.json();
      if(!data.sucesso) throw new Error(data.erro);
      toast(data.instancias_criadas===0 ? 'Tudo já sincronizado ✓' : `${data.instancias_criadas} questão(ões) sincronizadas! ✓`);
    } catch(e) { toast('Erro: '+e.message,'error'); }
  }

  function editarQuestao(id) {
    const q = questoesCache.find(x=>x.id===id); if(!q) return;
    document.getElementById('edit-id').value=q.id;
    document.getElementById('edit-nome').value=q.nome;
    document.getElementById('edit-enunciado').value=q.conteudo?.enunciado||q.conteudo?.texto_base||'';
    document.getElementById('edit-tipo').value=q.tipo;
    editTipoChanged();
    const c = q.conteudo||{};
    if(q.tipo!=='entrada-texto') {
      const alts=c.alternativas||[];
      const container=document.getElementById('edit-alternativas-container');
      container.innerHTML='';
      const lista=alts.length?alts:['','','',''];
      lista.forEach((texto,i)=>{
        const div=document.createElement('div'); div.className='alternativa-row';
        div.innerHTML=`<input type="radio" name="edit-gabarito" value="${i}" ${i===c.gabarito?'checked':''}> <label>${LETRAS[i]}</label><input type="text" value="${texto}" placeholder="Alternativa ${LETRAS[i]}">`;
        container.appendChild(div);
      });
    } else {
      document.getElementById('edit-gabarito').value=c.gabarito||'';
    }
    document.getElementById('modalEditarQuestao').classList.add('active');
  }
  function fecharEditarQuestao() { document.getElementById('modalEditarQuestao').classList.remove('active'); }
  function editTipoChanged() {
    const tipo=document.getElementById('edit-tipo').value;
    document.getElementById('edit-bloco-alternativas').style.display=tipo==='entrada-texto'?'none':'block';
    document.getElementById('edit-bloco-gabarito').style.display=tipo==='entrada-texto'?'block':'none';
  }
  function editAdicionarAlternativa() {
    const c=document.getElementById('edit-alternativas-container');
    const idx=c.children.length; if(idx>=8){toast('Máximo 8','error');return;}
    const div=document.createElement('div'); div.className='alternativa-row';
    div.innerHTML=`<input type="radio" name="edit-gabarito" value="${idx}"> <label>${LETRAS[idx]}</label><input type="text" placeholder="${LETRAS[idx]}">`;
    c.appendChild(div);
  }
  async function salvarEdicao() {
    const id=parseInt(document.getElementById('edit-id').value);
    const nome=document.getElementById('edit-nome').value.trim();
    const tipo=document.getElementById('edit-tipo').value;
    const enunciado=document.getElementById('edit-enunciado').value.trim();
    if(!nome){toast('Informe o nome','error');return;}
    if(!enunciado){toast('Informe o enunciado','error');return;}
    let conteudo={enunciado};
    if(tipo!=='entrada-texto') {
      const rows=document.querySelectorAll('#edit-alternativas-container .alternativa-row');
      const alternativas=[]; let gabarito=null;
      rows.forEach((row,i)=>{
        const radio=row.querySelector('input[type=radio]');
        const txt=row.querySelector('input[type=text]').value.trim();
        alternativas.push(txt||`Alternativa ${LETRAS[i]}`);
        if(radio.checked) gabarito=i;
      });
      if(gabarito===null){toast('Marque a alternativa correta','error');return;}
      conteudo.alternativas=alternativas; conteudo.gabarito=gabarito;
    } else {
      conteudo.gabarito=document.getElementById('edit-gabarito').value.trim();
    }
    try {
      const r=await fetch(`/api/professor/questoes/${id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({nome,tipo,conteudo})});
      const data=await r.json();
      if(!data.sucesso) throw new Error(data.erro||JSON.stringify(data));
      toast('Questão atualizada! ✓'); fecharEditarQuestao(); carregarQuestoes();
    } catch(e){ toast('Erro: '+e.message,'error'); }
  }

  async function sair() {
    await fetch('/api/professor/logout',{method:'POST'}).catch(()=>{});
    sessionStorage.removeItem('professor'); sessionStorage.removeItem('professor_id');
    window.location.href='/login';
  }

  carregarTurmas();
