CREATE DATABASE IF NOT EXISTS farmacia;
USE farmacia;

-- Tabela de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    telefone VARCHAR(20) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    numero VARCHAR(10) NOT NULL,
    bairro VARCHAR(100),
    complemento VARCHAR(100),
    produto_desejo VARCHAR(255),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Entregas
CREATE TABLE IF NOT EXISTS entregas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_cliente VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(300) NOT NULL,
    conteudo TEXT NOT NULL,
    status ENUM('Pendente', 'Entregue', 'Cancelado') DEFAULT 'Pendente',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);