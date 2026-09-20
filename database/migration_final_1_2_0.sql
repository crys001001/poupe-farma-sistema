-- Sistema de Cadastro 1.2.0 FINAL
-- Migração idempotente: pode ser executada novamente sem apagar registros.

CREATE DATABASE IF NOT EXISTS farmacia
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE farmacia;

CREATE TABLE IF NOT EXISTS afericoes_pressao (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome_cliente VARCHAR(100) NOT NULL DEFAULT '',
    telefone VARCHAR(20) NOT NULL DEFAULT '',
    sistolica SMALLINT UNSIGNED NOT NULL,
    diastolica SMALLINT UNSIGNED NOT NULL,
    batimentos SMALLINT UNSIGNED NOT NULL,
    valor DECIMAL(10,2) NOT NULL DEFAULT 5.00,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_afericoes_data (data_criacao),
    INDEX idx_afericoes_telefone (telefone)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

SELECT
    CASE
        WHEN COUNT(*) = 1 THEN 'OK: tabela afericoes_pressao disponível'
        ELSE 'ERRO: tabela afericoes_pressao não encontrada'
    END AS resultado
FROM information_schema.tables
WHERE table_schema = 'farmacia'
  AND table_name = 'afericoes_pressao';
