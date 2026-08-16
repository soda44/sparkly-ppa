  function trocarTab(tab, btn) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.painel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('painel' + tab.charAt(0).toUpperCase() + tab.slice(1)).classList.add('active');
  }

  async function loginAluno() {
    const usuario = document.getElementById('alunoUsuario').value.trim();
    const senha   = document.getElementById('alunoSenha').value.trim();
    const erroEl  = document.getElementById('erroAluno');
    erroEl.style.display = 'none';
    try {
      const r = await fetch('/api/login', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ usuario, senha })
      });
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      sessionStorage.setItem('aluno', JSON.stringify(data.dados || data));
      sessionStorage.setItem('aluno_id', data.aluno_id);
      window.location.href = '/aluno-dashboard';
    } catch(e) { erroEl.textContent = e.message; erroEl.style.display = 'block'; }
  }

  async function loginProf() {
    const usuario = document.getElementById('profUsuario').value.trim();
    const senha   = document.getElementById('profSenha').value.trim();
    const erroEl  = document.getElementById('erroProfessor');
    erroEl.style.display = 'none';
    try {
      const r = await fetch('/api/professor/login', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ usuario, senha })
      });
      const data = await r.json();
      if (!data.sucesso) throw new Error(data.erro);
      sessionStorage.setItem('professor', JSON.stringify(data.dados));
      window.location.href = '/professor-dashboard';
    } catch(e) { erroEl.textContent = e.message; erroEl.style.display = 'block'; }
  }

  document.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const tab = document.querySelector('.tab.active').textContent.toLowerCase();
    if (tab === 'aluno') loginAluno(); else loginProf();
  });
