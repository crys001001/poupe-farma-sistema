-- Script de Criação do Banco de Dados - Poupe Farma

CREATE DATABASE IF NOT EXISTS farmacia;
USE farmacia;


-- TABELA: CLIENTES
-- Guarda o cadastro único de cada cliente

CREATE TABLE IF NOT EXISTS clientes (
    telefone VARCHAR(20) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(150) NOT NULL,
    numero VARCHAR(10),
    complemento VARCHAR(50)
);


-- TABELA: ENTREGAS
-- Guarda o histórico e a fila de despachos do motoboy

CREATE TABLE IF NOT EXISTS entregas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_cliente VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    endereco TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    status ENUM('Pendente', 'Entregue', 'Cancelado') DEFAULT 'Pendente',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);