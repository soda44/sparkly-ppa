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

  async function sair() {
    try { await fetch('/api/logout', {method:'POST'}); } catch(e) {}
    sessionStorage.clear(); window.location.href='/login';
  }
