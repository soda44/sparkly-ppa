/**
 * Utilitários de gamificação compartilhados entre as páginas do aluno.
 * Mantém os badges de corações/pontos da navbar sincronizados com o
 * sessionStorage e com as respostas mais recentes da API.
 */

function obterAlunoDaSessao() {
  const bruto = sessionStorage.getItem('aluno');
  if (!bruto) return null;
  const dados = JSON.parse(bruto);
  return dados.aluno || dados;
}

function atualizarBadgesGamificacao(aluno) {
  if (!aluno) return;
  const elCoracoes = document.getElementById('navCoracoes');
  const elPontos = document.getElementById('navPontos');
  const elSparks = document.getElementById('navSparks');
  const max = aluno.coracoesMax || 5;
  if (elCoracoes) {
    elCoracoes.textContent = `❤️ ${aluno.coracoes ?? max}`;
    elCoracoes.classList.toggle('gami-badge-vazio', (aluno.coracoes ?? max) <= 0);
  }
  if (elPontos) elPontos.textContent = `⭐ ${aluno.pontos ?? 0}`;
  if (elSparks) elSparks.textContent = `⚡ ${aluno.sparks ?? 0}`;
}

/** Mescla novos campos (pontos/coracoes) no aluno salvo em sessionStorage e atualiza a navbar. */
function salvarGamificacaoNaSessao(camposAtualizados) {
  const bruto = sessionStorage.getItem('aluno');
  const dados = bruto ? JSON.parse(bruto) : { aluno: {} };
  const base = dados.aluno ? dados : { aluno: dados };
  base.aluno = { ...(base.aluno || {}), ...camposAtualizados };
  sessionStorage.setItem('aluno', JSON.stringify(base));
  atualizarBadgesGamificacao(base.aluno);
  return base.aluno;
}

document.addEventListener('DOMContentLoaded', () => {
  atualizarBadgesGamificacao(obterAlunoDaSessao());
});
