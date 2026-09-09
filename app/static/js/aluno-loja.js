  const alunoStr = sessionStorage.getItem('aluno');
  if (!alunoStr) window.location.href = '/login';
  const alunoInfo = (JSON.parse(alunoStr).aluno) || JSON.parse(alunoStr);
  document.getElementById('nomeAluno').textContent = alunoInfo.nome || alunoInfo.usuario;

  const SPARKS_PARA_RECARGA = 10;
  let alunoAtual = null;

  async function carregar() {
    try {
      const r = await fetch('/api/aluno');
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      alunoAtual = data.dados.aluno;
      salvarGamificacaoNaSessao(alunoAtual);
      atualizarItem();
    } catch(e) {
      mostrarErro('Não foi possível carregar seus dados.');
    }
  }

  function atualizarItem() {
    const cheio = alunoAtual.coracoes >= (alunoAtual.coracoesMax || 5);
    const semSparks = alunoAtual.sparks < SPARKS_PARA_RECARGA;
    const btn = document.getElementById('btnRecarregar');
    const btnTexto = document.getElementById('btnRecarregarTexto');
    const desc = document.getElementById('lojaDescCoracoes');

    desc.textContent = `Você tem ${alunoAtual.coracoes}/${alunoAtual.coracoesMax || 5} corações e ${alunoAtual.sparks} Sparks.`;

    if (cheio) {
      btn.disabled = true;
      btnTexto.textContent = 'Cheio';
    } else {
      btn.disabled = semSparks;
      btnTexto.innerHTML = `⚡ ${SPARKS_PARA_RECARGA}`;
    }
  }

  async function recarregar() {
    esconderMensagens();
    const btn = document.getElementById('btnRecarregar');
    btn.disabled = true;
    try {
      const r = await fetch('/api/aluno/loja/recarregar', { method: 'POST' });
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      alunoAtual = data.aluno;
      salvarGamificacaoNaSessao(alunoAtual);
      atualizarItem();
      mostrarSucesso('Corações recarregados com sucesso!');
    } catch(e) {
      mostrarErro(e.message);
      atualizarItem();
    }
  }

  function mostrarErro(msg) {
    const box = document.getElementById('erroBox');
    box.textContent = msg; box.style.display = 'block';
  }
  function mostrarSucesso(msg) {
    const box = document.getElementById('sucessoBox');
    box.textContent = msg; box.style.display = 'block';
  }
  function esconderMensagens() {
    document.getElementById('erroBox').style.display = 'none';
    document.getElementById('sucessoBox').style.display = 'none';
  }

  function sair() { sessionStorage.clear(); window.location.href='/login'; }

  // ─── Pet ───
  let petAtual = null;
  let coresAtuais = [];

  async function carregarPet() {
    try {
      const r = await fetch('/api/aluno/pet');
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      petAtual = data.pet;
      coresAtuais = data.cores;
      renderizarPet();
    } catch (e) {
      mostrarErro('Não foi possível carregar seu pet.');
    }
  }

  function renderizarPet() {
    const corInfo = coresAtuais.find(c => c.chave === petAtual.corAtual);
    document.getElementById('petBicho').style.setProperty('--pet-cor', corInfo ? corInfo.hex : '#FFC800');
    document.getElementById('petNomeExibicao').textContent = petAtual.nome;
    if (document.activeElement?.id !== 'petNomeInput') {
      document.getElementById('petNomeInput').value = petAtual.nome;
    }
    renderizarNivelPet();
    renderizarCoresGrid();
  }

  function renderizarNivelPet() {
    const nivel = petAtual.nivel;
    if (!nivel) return;
    document.getElementById('petNivelBadge').textContent = `Nível ${nivel.nivel}`;
    document.getElementById('petXpBarra').style.width = nivel.progresso + '%';
    document.getElementById('petXpLabel').textContent = nivel.nivel_maximo
      ? `Nível máximo! ${nivel.xp_atual} XP`
      : `${nivel.xp_atual} / ${nivel.xp_proximo_nivel} XP para o próximo nível`;
  }

  function renderizarCoresGrid() {
    const grid = document.getElementById('petCoresGrid');
    grid.innerHTML = '';
    coresAtuais.forEach(cor => {
      const btn = document.createElement('button');
      btn.className = 'pet-cor-item' + (cor.equipada ? ' equipada' : '');
      btn.type = 'button';

      let rodape;
      if (cor.equipada) {
        rodape = '<div class="pet-cor-selo">✓ Equipada</div>';
      } else if (cor.desbloqueada) {
        rodape = '<div class="pet-cor-selo">Usar</div>';
      } else {
        rodape = `<div class="pet-cor-custo">⚡ ${cor.custo}</div>`;
      }

      btn.innerHTML = `
        <div class="pet-cor-bolinha" style="background:${cor.hex}"></div>
        <div class="pet-cor-nome">${cor.nome}</div>
        ${rodape}
      `;
      btn.onclick = () => cor.desbloqueada ? equiparCor(cor.chave) : comprarCor(cor.chave);
      grid.appendChild(btn);
    });
  }

  async function salvarNomePet() {
    esconderMensagens();
    const nome = document.getElementById('petNomeInput').value.trim();
    if (!nome) { mostrarErro('Digite um nome para o seu pet.'); return; }
    try {
      const r = await fetch('/api/aluno/pet/nome', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome }),
      });
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      petAtual = data.pet;
      renderizarPet();
      mostrarSucesso('Nome do pet atualizado!');
    } catch (e) {
      mostrarErro(e.message);
    }
  }

  async function comprarCor(cor) {
    esconderMensagens();
    try {
      const r = await fetch('/api/aluno/pet/cor/comprar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cor }),
      });
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      petAtual = data.pet;
      alunoAtual = data.aluno;
      salvarGamificacaoNaSessao(alunoAtual);
      atualizarItem();
      await carregarPet();
      mostrarSucesso('Cor comprada e equipada no seu pet!');
    } catch (e) {
      mostrarErro(e.message);
    }
  }

  async function equiparCor(cor) {
    esconderMensagens();
    try {
      const r = await fetch('/api/aluno/pet/cor/equipar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cor }),
      });
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      petAtual = data.pet;
      renderizarPet();
    } catch (e) {
      mostrarErro(e.message);
    }
  }

  carregar();
  carregarPet();
