  const alunoStr = sessionStorage.getItem('aluno');
  if (!alunoStr) window.location.href = '/login';
  const alunoInfo = (JSON.parse(alunoStr).aluno) || JSON.parse(alunoStr);
  document.getElementById('nomeAluno').textContent = alunoInfo.nome || alunoInfo.usuario;

  const MEDALHAS = { 1: '🥇', 2: '🥈', 3: '🥉' };

  async function carregar() {
    try {
      const [rr, ra] = await Promise.all([
        fetch('/api/aluno/ranking'),
        fetch('/api/aluno')
      ]);
      const data = await rr.json();
      const dadosAluno = await ra.json();
      if (!data.sucesso) throw new Error(data.erro);
      if (dadosAluno.sucesso) salvarGamificacaoNaSessao(dadosAluno.dados.aluno);
      renderizar(data.ranking);
    } catch(e) {
      document.getElementById('rankingList').innerHTML =
        `<div class="empty-state"><div class="em-text">Erro: ${e.message}</div></div>`;
    }
  }

  function renderizar(ranking) {
    const lista = document.getElementById('rankingList');
    if (!ranking.length) {
      lista.innerHTML = `<div class="empty-state"><div class="em-text">Ainda não há alunos no ranking</div></div>`;
      return;
    }
    lista.innerHTML = ranking.map(r => {
      const souEu = r.usuario === alunoInfo.usuario;
      const posClasse = r.posicao === 1 ? 'top1' : r.posicao === 2 ? 'top2' : r.posicao === 3 ? 'top3' : '';
      const inicial = (r.nome || r.usuario || '?').trim().charAt(0).toUpperCase();
      return `
        <div class="ranking-item ${souEu ? 'voce' : ''}">
          <div class="ranking-posicao ${posClasse}">${MEDALHAS[r.posicao] || r.posicao}</div>
          <div class="ranking-avatar">${inicial}</div>
          <div class="ranking-nome">${r.nome}${souEu ? ' (você)' : ''}</div>
          <div class="ranking-pontos">${r.pontos} XP</div>
        </div>`;
    }).join('');
  }

  function sair() { sessionStorage.clear(); window.location.href='/login'; }
  carregar();
