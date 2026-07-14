CREATE DATABASE IF NOT EXISTS farmacia
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE farmacia;

-- ============================================================
-- TABELA DE CLIENTES
-- Telefone e nome são obrigatórios.
-- Todos os dados de endereço são opcionais.
-- ============================================================

CREATE TABLE IF NOT EXISTS clientes (
    telefone VARCHAR(20) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(200) NOT NULL DEFAULT '',
    numero VARCHAR(20) NOT NULL DEFAULT '',
    bairro VARCHAR(100) NOT NULL DEFAULT '',
    complemento VARCHAR(150) NOT NULL DEFAULT '',
    produto_desejo VARCHAR(255) NOT NULL DEFAULT '',
    data_cadastro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (telefone),
    INDEX idx_clientes_nome (nome),
    INDEX idx_clientes_data_cadastro (data_cadastro)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;


-- ============================================================
-- TABELA DE ENTREGAS
-- Os dados do cliente são armazenados na entrega para preservar
-- o histórico mesmo que o cadastro seja editado ou removido.
-- ============================================================

CREATE TABLE IF NOT EXISTS entregas (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome_cliente VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(300) NOT NULL DEFAULT 'Endereço não informado',
    conteudo TEXT NOT NULL,
    status ENUM(
        'Pendente',
        'Entregue',
        'Cancelado'
    ) NOT NULL DEFAULT 'Pendente',
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_entregas_telefone (telefone),
    INDEX idx_entregas_status_data (status, data_criacao),
    INDEX idx_entregas_data_criacao (data_criacao)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;