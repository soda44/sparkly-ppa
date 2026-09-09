"""Constantes do sistema de gamificação do Sparkly.

Inspirado no modelo de corações/pontos do Duolingo: o aluno tem um número
limitado de "vidas" (corações) que se recuperam praticando questões já
respondidas corretamente, ou podem ser recarregadas na loja com Sparks
acumulados ao acertar questões.

O Sparkly também tem pontos (XP), usados nas Missões e no Ranking. XP e
Sparks são ganhos juntos ao acertar uma questão, mas só os Sparks são
gastos na loja — o XP é apenas um indicador de progresso (por enquanto,
sem outro uso).
"""

# Quantidade máxima de corações (vidas) que um aluno pode ter.
MAX_CORACOES = 5

# Pontos (XP) ganhos ao acertar uma questão.
PONTOS_POR_QUESTAO = 10

# Sparks (⚡) ganhos ao acertar uma questão.
SPARKS_POR_QUESTAO = 5

# Custo em Sparks para recarregar os corações na loja.
SPARKS_PARA_RECARGA = 10

# Metas de pontos (XP) usadas na tela de Missões. Cada valor gera uma missão
# "Ganhe N XP" cujo progresso é calculado a partir do total de pontos do aluno.
MISSOES = [20, 50, 100, 250, 500, 1000]

# ──────────────────────────────────────────────
#  Pet (mascote): nome padrão e catálogo de cores da loja
# ──────────────────────────────────────────────

PET_NOME_PADRAO = 'Sparkly'

# Chave da cor que todo aluno já começa com (não pode ser comprada de novo).
PET_COR_PADRAO = 'amarelo'

# Catálogo de cores disponíveis na loja. Cada cor tem um nome de exibição,
# um valor hexadecimal usado para pintar o pet e um custo em Sparks
# (a cor padrão custa 0, pois já vem desbloqueada).
PET_CORES = {
    'amarelo':   {'nome': 'Amarelo Clássico', 'hex': '#FFC800', 'custo': 0},
    'verde':     {'nome': 'Verde Esperança',  'hex': '#58CC02', 'custo': 15},
    'azul':      {'nome': 'Azul Oceano',      'hex': '#1CB0F6', 'custo': 15},
    'laranja':   {'nome': 'Laranja Vibrante', 'hex': '#FF9600', 'custo': 20},
    'rosa':      {'nome': 'Rosa Choque',      'hex': '#FF4B9C', 'custo': 20},
    'roxo':      {'nome': 'Roxo Místico',     'hex': '#A560E8', 'custo': 20},
    'vermelho':  {'nome': 'Vermelho Fogo',    'hex': '#FF4B4B', 'custo': 25},
    'preto':     {'nome': 'Preto Elegante',   'hex': '#3C3C3C', 'custo': 30},
}

# Tamanho máximo permitido para o nome do pet.
PET_NOME_TAMANHO_MAX = 20

# ──────────────────────────────────────────────
#  Pet: níveis
# ──────────────────────────────────────────────

# Limiares de XP (pontos) para o pet subir de nível. Com 0 XP o pet começa
# no nível 1; ao atingir o 1º valor da lista ele sobe para o nível 2; ao
# atingir o 2º valor, para o nível 3; e assim por diante. Quando o aluno
# ultrapassa o último limiar, o pet fica no nível máximo (len(NIVEIS_PET) + 1).
NIVEIS_PET = [50, 120, 220, 350, 500, 700, 950, 1250, 1600, 2000]


def nivel_do_pet(pontos):
    """Calcula o nível do pet e o progresso até o próximo nível a partir do
    total de XP (pontos) do aluno.

    Retorna um dict com:
    - nivel: nível atual do pet (começa em 1).
    - xp_atual: XP total do aluno.
    - xp_proximo_nivel: limiar absoluto de XP para o próximo nível (None se
      o pet já está no nível máximo).
    - progresso: percentual (0-100) de progresso dentro do nível atual.
    - nivel_maximo: True se o pet já atingiu o maior nível possível.
    """
    pontos = pontos or 0
    limiar_anterior = 0
    for indice, limiar in enumerate(NIVEIS_PET):
        if pontos < limiar:
            faixa = limiar - limiar_anterior
            progresso = round(((pontos - limiar_anterior) / faixa) * 100, 1) if faixa else 100.0
            return {
                'nivel': indice + 1,
                'xp_atual': pontos,
                'xp_proximo_nivel': limiar,
                'progresso': progresso,
                'nivel_maximo': False,
            }
        limiar_anterior = limiar

    return {
        'nivel': len(NIVEIS_PET) + 1,
        'xp_atual': pontos,
        'xp_proximo_nivel': None,
        'progresso': 100.0,
        'nivel_maximo': True,
    }
