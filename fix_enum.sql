-- =====================================================
-- FIX 1: Remove a Foreign Key incorreta em desempenho
-- (id_atividade estava apontando para licao, mas deve
--  apontar para questao_instanciada)
-- =====================================================
ALTER TABLE desempenho DROP FOREIGN KEY desempenho_ibfk_2;

ALTER TABLE desempenho 
  ADD CONSTRAINT desempenho_ibfk_2 
  FOREIGN KEY (id_atividade) REFERENCES questao_instanciada(id);

-- =====================================================
-- FIX 2: (Opcional) Se quiser padronizar o ENUM de status
-- O banco já tem ('Concluida','Pendente','Em andamento')
-- O código foi corrigido para usar esses valores exatos
-- Só rode isso se quiser alterar os nomes do ENUM
-- =====================================================
-- ALTER TABLE desempenho 
--   MODIFY COLUMN status ENUM('Concluida','Pendente','Em andamento') NOT NULL DEFAULT 'Pendente';

-- Verificação
SHOW CREATE TABLE desempenho;
