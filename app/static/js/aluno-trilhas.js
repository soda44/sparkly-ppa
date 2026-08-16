  const alunoStr = sessionStorage.getItem('aluno');
  if (!alunoStr) window.location.href = '/login';
  const aluno = JSON.parse(alunoStr);
  document.getElementById('nomeAluno').textContent = aluno.nome || aluno.usuario;

  const TIPO_LABEL = {
    multipla_escolha:'Múltipla Escolha','multipla-escolha':'Múltipla Escolha',
    verdadeiro_falso:'V/F', dissertativa:'Dissertativa', calculo:'Cálculo'
  };
  const TIPO_BADGE = {
    multipla_escolha:'badge-blue','multipla-escolha':'badge-blue',
    verdadeiro_falso:'badge-purple', dissertativa:'badge-neutral', calculo:'badge-green'
  };

  let todasQuestoes = [];

  async function carregar() {
    try {
      const r = await fetch('/api/aluno/questoes');
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      todasQuestoes = data.questoes;
      renderizar(todasQuestoes);
    } catch(e) {
      document.getElementById('questoesGrid').innerHTML =
        `<div class="empty" style="grid-column:1/-1"><div class="em-icon"></div><div class="em-text">Erro: ${e.message}</div></div>`;
    }
  }

  function filtrar(tipo, btn) {
    document.querySelectorAll('.filtro-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    let lista = todasQuestoes;
    if (tipo==='pendente')   lista = todasQuestoes.filter(q => !q.ja_respondida);
    else if (tipo==='respondida') lista = todasQuestoes.filter(q => q.ja_respondida);
    else if (tipo!=='todos') lista = todasQuestoes.filter(q => q.tipo===tipo||q.tipo===tipo.replace('_','-'));
    renderizar(lista);
  }

  function renderizar(questoes) {
    const grid = document.getElementById('questoesGrid');
    if (!questoes.length) {
      grid.innerHTML=`<div class="empty" style="grid-column:1/-1"><div class="em-icon"></div><div class="em-text">Nenhuma questão encontrada</div></div>`;
      return;
    }
    grid.innerHTML = questoes.map(q => `
      <div class="questao-card ${q.ja_respondida?'respondida':''}" onclick="abrirQuestao(${q.id})">
        <div class="q-header">
          <div class="q-nome">${q.nome}</div>
          <span class="badge ${q.ja_respondida?'badge-green':'badge-yellow'}">
            ${q.ja_respondida?'✓ Feita':'Nova'}
          </span>
        </div>
        <div class="q-tipo-row">
          <span class="badge ${TIPO_BADGE[q.tipo]||'badge-neutral'}">${TIPO_LABEL[q.tipo]||q.tipo}</span>
        </div>
        <div class="q-preview">${q.conteudo.enunciado||''}</div>
        <button class="btn ${q.ja_respondida?'btn-outline':'btn-primary'} btn-sm btn-full">
          ${q.ja_respondida?'Refazer':'Resolver →'}
        </button>
      </div>`).join('');
  }

  function abrirQuestao(id) { window.location.href=`/aluno-desafio?questao=${id}`; }
  function sair() { sessionStorage.clear(); window.location.href='/login'; }
  carregar();
