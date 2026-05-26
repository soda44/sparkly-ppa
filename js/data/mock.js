const ALUNO = {
  nome: "Maria Silva",
  nivel: 3,
  xp: 340,
  xpProximoNivel: 500,
  acertos: 18,
  erros: 5
};

const MODULOS = [
  { id: 1, titulo: "Eletrização por Atrito",  desbloqueado: true,  progresso: 100 },
  { id: 2, titulo: "Eletrização por Contato", desbloqueado: true,  progresso: 60  },
  { id: 3, titulo: "Eletrização por Indução", desbloqueado: false, progresso: 0   },
  { id: 4, titulo: "Lei de Coulomb",          desbloqueado: false, progresso: 0   }
];

const QUESTOES = {
  1: [
    {
      enunciado: "Quando atritamos um bastão de vidro com seda, o bastão fica com carga...",
      alternativas: ["Negativa", "Positiva", "Neutra", "Depende da temperatura"],
      correta: 1
    },
    {
      enunciado: "A eletrização por atrito ocorre pois corpos diferentes têm diferentes...",
      alternativas: ["Massas atômicas", "Afinidades eletrônicas", "Cargas nucleares", "Pressões internas"],
      correta: 1
    }
  ],
  2: [
    {
      enunciado: "Na eletrização por contato, o corpo que toca o condutor eletrizado...",
      alternativas: ["Perde toda a carga", "Adquire carga do mesmo sinal", "Adquire carga de sinal oposto", "Fica neutro"],
      correta: 1
    },
    {
      enunciado: "Para que a eletrização por contato ocorra, os corpos devem ser...",
      alternativas: ["Isolantes", "Condutores", "Magnéticos", "Radioativos"],
      correta: 1
    }
  ]
};
