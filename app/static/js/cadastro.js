  let usaNomeSocial = false;

  function definirUsaNomeSocial(valor) {
    usaNomeSocial = valor;
    document.getElementById('btnNomeSocialSim').classList.toggle('selecionado', valor);
    document.getElementById('btnNomeSocialNao').classList.toggle('selecionado', !valor);
    document.getElementById('grupoNomeSocial').style.display = valor ? 'block' : 'none';
    if (!valor) document.getElementById('nomeSocial').value = '';
    atualizarBarra();
  }

  function atualizarGenero() {
    const generoSelecionado = document.querySelector('input[name="genero"]:checked');
    const ehPersonalizado = generoSelecionado && generoSelecionado.value === 'personalizado';
    document.getElementById('grupoGeneroPersonalizado').style.display = ehPersonalizado ? 'block' : 'none';
    if (!ehPersonalizado) document.getElementById('generoPersonalizado').value = '';
    atualizarBarra();
  }

  function atualizarBarra() {
    const campos = ['nome','email','usuarioNovo','senhaNova','senhaConfirmar'];
    let preenchidos = campos.filter(id => document.getElementById(id).value.trim() !== '').length;
    let total = campos.length + 1; // +1 para o gênero

    if (document.querySelector('input[name="genero"]:checked')) preenchidos++;

    if (usaNomeSocial) {
      total++;
      if (document.getElementById('nomeSocial').value.trim() !== '') preenchidos++;
    }

    document.getElementById('progress').style.width = (preenchidos / total * 100) + '%';
  }

  async function realizarCadastro() {
    const nome     = document.getElementById('nome').value.trim();
    const email    = document.getElementById('email').value.trim();
    const usuario  = document.getElementById('usuarioNovo').value.trim();
    const senha    = document.getElementById('senhaNova').value.trim();
    const senhaConf= document.getElementById('senhaConfirmar').value.trim();
    const nomeSocial = document.getElementById('nomeSocial').value.trim();
    const generoSelecionado = document.querySelector('input[name="genero"]:checked');
    const genero = generoSelecionado ? generoSelecionado.value : '';
    const generoPersonalizado = document.getElementById('generoPersonalizado').value.trim();
    const erroMsg  = document.getElementById('erroMsg');
    const succMsg  = document.getElementById('sucessoMsg');
    erroMsg.style.display = 'none'; succMsg.style.display = 'none';

    if (!nome||!email||!usuario||!senha) { erroMsg.textContent='Todos os campos são obrigatórios.'; erroMsg.style.display='block'; return; }
    if (senha !== senhaConf) { erroMsg.textContent='As senhas não conferem.'; erroMsg.style.display='block'; return; }
    if (senha.length < 3) { erroMsg.textContent='A senha deve ter pelo menos 3 caracteres.'; erroMsg.style.display='block'; return; }
    if (!genero) { erroMsg.textContent='Selecione um gênero.'; erroMsg.style.display='block'; return; }
    if (genero === 'personalizado' && !generoPersonalizado) { erroMsg.textContent='Informe o gênero personalizado.'; erroMsg.style.display='block'; return; }
    if (usaNomeSocial && !nomeSocial) { erroMsg.textContent='Informe o nome social.'; erroMsg.style.display='block'; return; }

    try {
      const r = await fetch('/api/cadastro', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
          nome, email, usuario, senha,
          usaNomeSocial,
          nomeSocial: usaNomeSocial ? nomeSocial : null,
          genero,
          generoPersonalizado: genero === 'personalizado' ? generoPersonalizado : null
        })
      });
      const dados = await r.json();
      if (!r.ok) { erroMsg.textContent = dados.erro||'Erro ao cadastrar.'; erroMsg.style.display='block'; return; }
      succMsg.textContent = 'Conta criada! Redirecionando...';
      succMsg.style.display = 'block';
      setTimeout(() => window.location.href = '/login', 2000);
    } catch(e) { erroMsg.textContent = 'Erro na conexão.'; erroMsg.style.display='block'; }
  }

  document.addEventListener('keydown', e => { if(e.key==='Enter') realizarCadastro(); });
