  if (!sessionStorage.getItem('aluno')) window.location.href='/login';

  const LETRAS = ['A','B','C','D','E','F','G','H'];
  const TIPO_LABEL = {
    multipla_escolha:'Múltipla Escolha','multipla-escolha':'Múltipla Escolha',
    verdadeiro_falso:'Verdadeiro / Falso', dissertativa:'Dissertativa', calculo:'Cálculo'
  };
  const TIPO_BADGE = {
    multipla_escolha:'badge-blue','multipla-escolha':'badge-blue',
    verdadeiro_falso:'badge-purple', dissertativa:'badge-neutral', calculo:'badge-green'
  };

  const params = new URLSearchParams(window.location.search);
  const questaoId = parseInt(params.get('questao'));
  const licaoId = params.get('licao') ? parseInt(params.get('licao')) : null;
  if (!questaoId) window.location.href='/aluno-trilhas';

  let questaoAtual = null, respostaSelecionada = null, jaConfirmou = false;

  function proximaQuestaoDaFila() {
    if (!licaoId) return null;
    try {
      const estado = JSON.parse(sessionStorage.getItem('licaoAtual') || 'null');
      if (!estado || estado.licaoId !== licaoId) return null;
      const idx = estado.fila.indexOf(questaoId);
      if (idx === -1 || idx === estado.fila.length - 1) return null;
      return estado.fila[idx + 1];
    } catch (e) { return null; }
  }

  async function carregarQuestao() {
    try {
      const url = licaoId ? `/api/aluno/licoes/${licaoId}/questoes` : '/api/aluno/questoes';
      const r = await fetch(url);
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      const lista = licaoId ? data.questoes : data.questoes;
      questaoAtual = lista.find(q => q.id === questaoId);
      if (!questaoAtual) throw new Error('Questão não encontrada');

      if (questaoAtual.bloqueada) {
        document.getElementById('telaLoading').style.display = 'none';
        document.getElementById('telaBloqueada').style.display = 'flex';
        return;
      }
      renderQuestao();
    } catch(e) {
      document.getElementById('telaLoading').innerHTML =
        `<div style="text-align:center"><div style="font-size:2rem"></div><p style="font-weight:700;color:var(--red);margin:8px 0">${e.message}</p>
         <a href="/aluno-trilhas" class="btn btn-outline btn-sm mt-2">← Voltar</a></div>`;
    }
  }

  function renderQuestao() {
    document.getElementById('telaLoading').style.display = 'none';
    document.getElementById('telaQuestao').style.display = 'flex';
    const q = questaoAtual;
    const badge = document.getElementById('tipoBadge');
    badge.textContent = TIPO_LABEL[q.tipo] || q.tipo;
    badge.className = 'badge ' + (TIPO_BADGE[q.tipo] || 'badge-neutral');
    document.getElementById('qNome').textContent = q.nome;
    document.getElementById('qEnunciado').textContent = q.conteudo.enunciado || '';

    const tipo = q.tipo;
    if (tipo==='multipla_escolha'||tipo==='multipla-escolha'||tipo==='verdadeiro_falso') {
      const wrap = document.getElementById('alternativasWrap');
      const alts = q.conteudo.alternativas || [];
      wrap.innerHTML = alts.map((alt,i) => `
        <button class="alt-btn" id="alt-${i}" onclick="selecionarAlt(${i})">
          <span class="letra">${LETRAS[i]}</span><span>${alt}</span>
        </button>`).join('');
      wrap.style.display = 'flex';
      document.getElementById('respostaLivre').style.display = 'none';
    } else {
      document.getElementById('alternativasWrap').style.display = 'none';
      document.getElementById('respostaLivre').style.display = 'block';
    }
  }

  function selecionarAlt(idx) {
    if (jaConfirmou) return;
    respostaSelecionada = idx;
    document.querySelectorAll('.alt-btn').forEach((btn,i) => btn.classList.toggle('selecionada', i===idx));
    document.getElementById('btnConfirmar').disabled = false;
  }

  async function confirmar() {
    if (jaConfirmou) return;
    const tipo = questaoAtual.tipo;
    let resposta;
    if (tipo==='multipla_escolha'||tipo==='multipla-escolha'||tipo==='verdadeiro_falso') {
      if (respostaSelecionada===null) return;
      resposta = respostaSelecionada;
    } else {
      resposta = document.getElementById('respostaLivre').value.trim();
      if (!resposta) return;
    }

    jaConfirmou = true;
    document.getElementById('btnConfirmar').disabled = true;
    document.getElementById('respostaLivre').disabled = true;
    document.querySelectorAll('.alt-btn').forEach(b => b.disabled = true);

    try {
      const r = await fetch(`/api/aluno/questoes/${questaoId}/responder`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ resposta })
      });
      const data = await r.json();
      if (!data.sucesso) {
        if (r.status === 403) {
          document.getElementById('telaQuestao').style.display = 'none';
          document.getElementById('telaBloqueada').style.display = 'flex';
          return;
        }
        throw new Error(data.erro);
      }
      if (typeof data.pontos_totais === 'number' || typeof data.sparks_totais === 'number' || typeof data.coracoes === 'number') {
        const campos = {};
        if (typeof data.pontos_totais === 'number') campos.pontos = data.pontos_totais;
        if (typeof data.sparks_totais === 'number') campos.sparks = data.sparks_totais;
        if (typeof data.coracoes === 'number') campos.coracoes = data.coracoes;
        salvarGamificacaoNaSessao(campos);
      }
      mostrarFeedback(data);
      setTimeout(() => mostrarResultado(data), 2200);
    } catch(e) {
      const box = document.getElementById('feedbackBox');
      box.className = 'feedback-box incorreto'; box.style.display = 'block';
      document.getElementById('feedbackTitulo').textContent = 'Erro';
      document.getElementById('feedbackDetalhe').textContent = e.message;
      jaConfirmou = false;
      document.getElementById('btnConfirmar').disabled = false;
    }
  }

  function mostrarFeedback(data) {
    const box = document.getElementById('feedbackBox');
    const alts = questaoAtual.conteudo.alternativas || [];
    const tipo = questaoAtual.tipo;
    box.className = 'feedback-box ' + (data.correto ? 'correto' : 'incorreto');
    box.style.display = 'block';
    document.getElementById('feedbackTitulo').textContent = data.correto ? '✓ Correto!' : '✗ Resposta incorreta';
    if (tipo==='multipla_escolha'||tipo==='multipla-escolha'||tipo==='verdadeiro_falso') {
      document.querySelectorAll('.alt-btn').forEach((btn,i) => {
        if (i===data.gabarito) btn.classList.add('correta');
        else if (i===respostaSelecionada && !data.correto) btn.classList.add('errada');
      });
      document.getElementById('feedbackDetalhe').textContent = data.correto
        ? 'Parabéns! Continue assim! '
        : `Resposta correta: ${LETRAS[data.gabarito]}) ${alts[data.gabarito]||''}`;
    } else {
      document.getElementById('feedbackDetalhe').textContent = data.correto
        ? 'Resposta certa! ' : `Gabarito: "${data.gabarito}"`;
    }
  }

  function mostrarResultado(data) {
    document.getElementById('telaQuestao').style.display = 'none';
    document.getElementById('telaResultado').style.display = 'flex';
    document.getElementById('resEmoji').textContent = data.correto ? '' : '';
    document.getElementById('resTitulo').textContent = data.correto ? 'Incrível!' : 'Quase lá!';
    document.getElementById('resTitulo').className = 'resultado-titulo ' + (data.correto?'correto':'incorreto');
    document.getElementById('resSub').textContent = data.correto
      ? 'Nota 10! Você está arrasando! Continue assim!'
      : 'Não desanime! Refaça a questão para melhorar.';
    const fill = document.getElementById('resBarraFill');
    fill.style.background = data.correto ? 'var(--green)' : 'var(--red)';
    setTimeout(() => fill.style.width = (data.correto?'100%':'30%'), 100);
    document.getElementById('resBarraLabel').textContent = data.correto ? 'Nota: 10.0' : 'Nota: 0.0';

    const gami = document.getElementById('resGamificacao');
    const partes = [];
    if (data.pontos_ganhos) partes.push(`<span class="ganho-pontos">⭐ +${data.pontos_ganhos} XP</span>`);
    if (data.sparks_ganhos) partes.push(`<span class="ganho-sparks">⚡ +${data.sparks_ganhos} Sparks</span>`);
    if (data.correto && data.em_pratica) partes.push(`<span class="ganho-coracao">❤️ +1 coração</span>`);
    else if (!data.correto && !data.em_pratica) partes.push(`<span class="perda-coracao">💔 -1 coração</span>`);
    if (data.pet_subiu_nivel && data.pet_nivel) {
      partes.push(`<span class="ganho-nivel-pet">🐾 Seu pet subiu para o nível ${data.pet_nivel.nivel}!</span>`);
    }
    gami.innerHTML = partes.join('');

    const proximaId = proximaQuestaoDaFila();
    const acoes = document.querySelector('#telaResultado .resultado-acoes');
    if (proximaId) {
      acoes.innerHTML = `
        <button class="btn btn-primary btn-full btn-lg" onclick="irParaProximaQuestao(${proximaId})">Próxima questão →</button>
        <a href="/aluno-trilhas" class="btn btn-outline btn-full">Sair da lição</a>`;
    } else if (licaoId) {
      acoes.innerHTML = `
        <a href="/aluno-trilhas" class="btn btn-primary btn-full btn-lg">🎉 Lição concluída! Ver trilha</a>
        <a href="/aluno-dashboard" class="btn btn-outline btn-full">Dashboard</a>`;
    }
  }

  function irParaProximaQuestao(id) {
    window.location.href = `/aluno-desafio?questao=${id}&licao=${licaoId}`;
  }

  document.getElementById('respostaLivre').addEventListener('input', function() {
    document.getElementById('btnConfirmar').disabled = this.value.trim()==='';
  });

  carregarQuestao();
