  function atualizarBarra() {
    const campos = ['nome','email','usuarioNovo','senhaNova','senhaConfirmar'];
    const preenchidos = campos.filter(id => document.getElementById(id).value.trim() !== '').length;
    document.getElementById('progress').style.width = (preenchidos / campos.length * 100) + '%';
  }

  async function realizarCadastro() {
    const nome     = document.getElementById('nome').value.trim();
    const email    = document.getElementById('email').value.trim();
    const usuario  = document.getElementById('usuarioNovo').value.trim();
    const senha    = document.getElementById('senhaNova').value.trim();
    const senhaConf= document.getElementById('senhaConfirmar').value.trim();
    const erroMsg  = document.getElementById('erroMsg');
    const succMsg  = document.getElementById('sucessoMsg');
    erroMsg.style.display = 'none'; succMsg.style.display = 'none';

    if (!nome||!email||!usuario||!senha) { erroMsg.textContent='Todos os campos são obrigatórios.'; erroMsg.style.display='block'; return; }
    if (senha !== senhaConf) { erroMsg.textContent='As senhas não conferem.'; erroMsg.style.display='block'; return; }
    if (senha.length < 3) { erroMsg.textContent='A senha deve ter pelo menos 3 caracteres.'; erroMsg.style.display='block'; return; }

    try {
      const r = await fetch('/api/cadastro', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ nome, email, usuario, senha })
      });
      const dados = await r.json();
      if (!r.ok) { erroMsg.textContent = dados.erro||'Erro ao cadastrar.'; erroMsg.style.display='block'; return; }
      succMsg.textContent = 'Conta criada! Redirecionando...';
      succMsg.style.display = 'block';
      setTimeout(() => window.location.href = '/login', 2000);
    } catch(e) { erroMsg.textContent = 'Erro na conexão.'; erroMsg.style.display='block'; }
  }

  document.addEventListener('keydown', e => { if(e.key==='Enter') realizarCadastro(); });
