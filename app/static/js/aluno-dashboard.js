  const _stored = JSON.parse(sessionStorage.getItem('aluno'));
  if (!_stored) window.location.href = '/login';
  const alunoInfo = _stored.aluno || _stored;
  const nome = alunoInfo.nome || alunoInfo.usuario || '—';
  const primeiroNome = nome.split(' ')[0];
  document.getElementById('nomeAluno').textContent = nome;
  document.getElementById('nomeHero').textContent  = primeiroNome;

  async function carregarDados() {
    try {
      const r = await fetch('/api/aluno');
      const resultado = await r.json();
      if (!resultado.sucesso) { window.location.href='/login'; return; }
      const d = resultado.dados;
      document.getElementById('statConcluidas').textContent = d.desempenho.atividades_completas;
      document.getElementById('statMedia').textContent      = d.desempenho.media_notas.toFixed(1);
      document.getElementById('statTotal').textContent      = d.desempenho.total_atividades;

      salvarGamificacaoNaSessao(d.aluno);
      carregarMissaoDestaque();

      const lista = document.getElementById('licoesList');
      if (!d.licoes || d.licoes.length === 0) {
        lista.innerHTML = `<div class="empty-state"><div class="em-text">Nenhuma lição disponível ainda</div></div>`;
        return;
      }
      lista.innerHTML = d.licoes.slice(0,5).map(l => `
        <div class="licao-item">
          <div>
            <div class="l-tipo">${l.tipo||'Lição'}</div>
            <div class="l-desc">${l.descricao||'Sem descrição'}</div>
          </div>
          <span class="badge badge-green">Ver</span>
        </div>`).join('');
    } catch(e) {
      document.getElementById('licoesList').innerHTML = `<div class="empty-state"><div class="em-text">Erro ao carregar</div></div>`;
    }
  }
  carregarDados();

  async function carregarMeuPet() {
    try {
      const r = await fetch('/api/aluno/pet');
      const data = await r.json();
      if (!data.sucesso) return;
      const corInfo = data.cores.find(c => c.chave === data.pet.corAtual);
      document.getElementById('meuPetBicho').style.setProperty('--pet-cor', corInfo ? corInfo.hex : '#FFC800');
      document.getElementById('meuPetNome').textContent = data.pet.nome;
      if (data.pet.nivel) {
        document.getElementById('meuPetNivel').textContent = `Nível ${data.pet.nivel.nivel}`;
      }
    } catch (e) { /* silencioso: widget opcional */ }
  }
  carregarMeuPet();

  async function carregarMissaoDestaque() {
    try {
      const r = await fetch('/api/aluno/missoes');
      const data = await r.json();
      if (!data.sucesso) return;
      const proxima = data.missoes.find(m => !m.concluida) || data.missoes[data.missoes.length - 1];
      document.getElementById('missaoTitulo').textContent =
        `${proxima.titulo} (${proxima.pontos_atuais}/${proxima.meta} XP)`;
      setTimeout(() => {
        document.getElementById('missaoBarra').style.width = proxima.progresso + '%';
      }, 100);
    } catch(e) {
      document.getElementById('missaoTitulo').textContent = 'Não foi possível carregar sua missão';
    }
  }

  async function sair() {
    try { await fetch('/api/logout', {method:'POST'}); } catch(e) {}
    sessionStorage.clear(); window.location.href='/login';
  }
