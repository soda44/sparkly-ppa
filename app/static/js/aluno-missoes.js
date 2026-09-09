  const alunoStr = sessionStorage.getItem('aluno');
  if (!alunoStr) window.location.href = '/login';
  const alunoInfo = (JSON.parse(alunoStr).aluno) || JSON.parse(alunoStr);
  document.getElementById('nomeAluno').textContent = alunoInfo.nome || alunoInfo.usuario;

  async function carregar() {
    try {
      const [rm, ra] = await Promise.all([
        fetch('/api/aluno/missoes'),
        fetch('/api/aluno')
      ]);
      const data = await rm.json();
      const dadosAluno = await ra.json();
      if (!data.sucesso) throw new Error(data.erro);
      if (dadosAluno.sucesso) salvarGamificacaoNaSessao(dadosAluno.dados.aluno);
      renderizar(data.missoes);
    } catch(e) {
      document.getElementById('missoesList').innerHTML =
        `<div class="empty-state"><div class="em-text">Erro: ${e.message}</div></div>`;
    }
  }

  function renderizar(missoes) {
    const lista = document.getElementById('missoesList');
    if (!missoes.length) {
      lista.innerHTML = `<div class="empty-state"><div class="em-text">Nenhuma missão disponível</div></div>`;
      return;
    }
    lista.innerHTML = missoes.map(m => `
      <div class="missao-card ${m.concluida ? 'concluida' : ''}">
        <div class="missao-icone">${m.concluida ? '🏆' : '⭐'}</div>
        <div class="missao-info">
          <div class="missao-titulo">${m.titulo}</div>
          <div class="xp-bar-wrap"><div class="xp-bar" style="width:${m.progresso}%"></div></div>
          <div class="missao-legenda">${Math.min(m.pontos_atuais, m.meta)} / ${m.meta} XP${m.concluida ? ' · Concluída!' : ''}</div>
        </div>
      </div>`).join('');
  }

  function sair() { sessionStorage.clear(); window.location.href='/login'; }
  carregar();
