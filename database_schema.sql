-- ============================================
-- Sistema MIRO - Database Schema
-- ============================================

-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS `sistema_miro` 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_0900_ai_ci;

-- Usar o banco de dados
USE `sistema_miro`;

-- ============================================
-- Tabela de Departamentos
-- ============================================
CREATE TABLE IF NOT EXISTS `departamentos` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `nome` VARCHAR(100) UNIQUE NOT NULL,
    `descricao` TEXT,
    `data_criacao` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================
-- Tabela de Funcionários
-- ============================================
CREATE TABLE IF NOT EXISTS `funcionarios` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `nome` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) UNIQUE NOT NULL,
    `data_nascimento` DATE,
    `telefone` VARCHAR(20),
    `cargo` VARCHAR(100),
    `salario` DECIMAL(10,2),
    `observacoes` TEXT,
    `departamento_id` INT,
    `data_criacao` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`departamento_id`) REFERENCES `departamentos`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================
-- Tabela de Usuários do Sistema
-- ============================================
CREATE TABLE IF NOT EXISTS `usuarios` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `nome` VARCHAR(100) NOT NULL,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `senha_hash` VARCHAR(128) NOT NULL,
    `nivel_acesso` VARCHAR(20) NOT NULL DEFAULT 'user',
    `data_criacao` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================
-- Tabela de Projetos
-- ============================================
CREATE TABLE IF NOT EXISTS `projetos` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `nome` VARCHAR(100) NOT NULL,
    `descricao` TEXT,
    `data_inicio` DATE,
    `data_fim` DATE,
    `status` VARCHAR(50) DEFAULT 'Em Andamento',
    `departamento_id` INT,
    `data_criacao` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`departamento_id`) REFERENCES `departamentos`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================
-- Tabela de Associação Funcionários-Projetos
-- ============================================
CREATE TABLE IF NOT EXISTS `funcionarios_projetos` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `funcionario_id` INT NOT NULL,
    `projeto_id` INT NOT NULL,
    `papel` VARCHAR(100),
    `data_inicio` DATE,
    `data_fim` DATE,
    `data_criacao` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`funcionario_id`) REFERENCES `funcionarios`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`projeto_id`) REFERENCES `projetos`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE KEY `unique_funcionario_projeto` (`funcionario_id`, `projeto_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================
-- Tabela de Contatos dos Funcionários
-- ============================================
CREATE TABLE IF NOT EXISTS `contatos_funcionarios` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `funcionario_id` INT NOT NULL,
    `tipo_contato` VARCHAR(50) NOT NULL, -- 'telefone', 'email', 'endereco', etc.
    `valor` VARCHAR(255) NOT NULL,
    `principal` BOOLEAN DEFAULT FALSE,
    `data_criacao` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`funcionario_id`) REFERENCES `funcionarios`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================
-- Inserir dados iniciais (opcional)
-- ============================================

-- Inserir departamentos padrão
INSERT IGNORE INTO `departamentos` (`nome`, `descricao`) VALUES
('Recursos Humanos', 'Departamento responsável pela gestão de pessoas'),
('Tecnologia da Informação', 'Departamento de desenvolvimento e suporte técnico'),
('Financeiro', 'Departamento de controle financeiro e contabilidade'),
('Comercial', 'Departamento de vendas e relacionamento com clientes'),
('Operações', 'Departamento de operações e logística');

-- Inserir usuário administrador padrão
-- Senha: admin123 (hash SHA-256)
INSERT IGNORE INTO `usuarios` (`nome`, `username`, `senha_hash`, `nivel_acesso`) VALUES
('Administrador do Sistema', 'admin', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'admin');

-- ============================================
-- Índices para melhor performance
-- ============================================

-- Índices para a tabela funcionarios
CREATE INDEX IF NOT EXISTS `idx_funcionarios_departamento` ON `funcionarios`(`departamento_id`);
CREATE INDEX IF NOT EXISTS `idx_funcionarios_email` ON `funcionarios`(`email`);
CREATE INDEX IF NOT EXISTS `idx_funcionarios_nome` ON `funcionarios`(`nome`);

-- Índices para a tabela projetos
CREATE INDEX IF NOT EXISTS `idx_projetos_departamento` ON `projetos`(`departamento_id`);
CREATE INDEX IF NOT EXISTS `idx_projetos_status` ON `projetos`(`status`);

-- Índices para a tabela funcionarios_projetos
CREATE INDEX IF NOT EXISTS `idx_func_proj_funcionario` ON `funcionarios_projetos`(`funcionario_id`);
CREATE INDEX IF NOT EXISTS `idx_func_proj_projeto` ON `funcionarios_projetos`(`projeto_id`);

-- Índices para a tabela contatos_funcionarios
CREATE INDEX IF NOT EXISTS `idx_contatos_funcionario` ON `contatos_funcionarios`(`funcionario_id`);
CREATE INDEX IF NOT EXISTS `idx_contatos_tipo` ON `contatos_funcionarios`(`tipo_contato`);

-- Índices para a tabela usuarios
CREATE INDEX IF NOT EXISTS `idx_usuarios_username` ON `usuarios`(`username`);
CREATE INDEX IF NOT EXISTS `idx_usuarios_nivel` ON `usuarios`(`nivel_acesso`);

-- ============================================
-- Views úteis para relatórios
-- ============================================

-- View para funcionários com departamento
CREATE OR REPLACE VIEW `view_funcionarios_completo` AS
SELECT 
    f.id,
    f.nome,
    f.email,
    f.data_nascimento,
    f.telefone,
    f.cargo,
    f.salario,
    f.observacoes,
    d.nome AS departamento_nome,
    d.descricao AS departamento_descricao,
    f.data_criacao
FROM `funcionarios` f
LEFT JOIN `departamentos` d ON f.departamento_id = d.id;

-- View para projetos com departamento
CREATE OR REPLACE VIEW `view_projetos_completo` AS
SELECT 
    p.id,
    p.nome,
    p.descricao,
    p.data_inicio,
    p.data_fim,
    p.status,
    d.nome AS departamento_nome,
    p.data_criacao,
    COUNT(fp.funcionario_id) AS total_funcionarios
FROM `projetos` p
LEFT JOIN `departamentos` d ON p.departamento_id = d.id
LEFT JOIN `funcionarios_projetos` fp ON p.id = fp.projeto_id
GROUP BY p.id, p.nome, p.descricao, p.data_inicio, p.data_fim, p.status, d.nome, p.data_criacao;

-- View para funcionários em projetos
CREATE OR REPLACE VIEW `view_funcionarios_projetos` AS
SELECT 
    fp.id,
    f.nome AS funcionario_nome,
    f.email AS funcionario_email,
    f.cargo AS funcionario_cargo,
    p.nome AS projeto_nome,
    p.status AS projeto_status,
    fp.papel,
    fp.data_inicio,
    fp.data_fim,
    d.nome AS departamento_nome
FROM `funcionarios_projetos` fp
JOIN `funcionarios` f ON fp.funcionario_id = f.id
JOIN `projetos` p ON fp.projeto_id = p.id
LEFT JOIN `departamentos` d ON f.departamento_id = d.id;

-- ============================================
-- Comentários finais
-- ============================================

/*
Este script SQL cria a estrutura completa do banco de dados para o Sistema MIRO.

Tabelas criadas:
1. departamentos - Armazena os departamentos da empresa
2. funcionarios - Cadastro de funcionários
3. usuarios - Usuários do sistema com controle de acesso
4. projetos - Cadastro de projetos
5. funcionarios_projetos - Associação entre funcionários e projetos
6. contatos_funcionarios - Contatos adicionais dos funcionários

Recursos incluídos:
- Chaves estrangeiras com integridade referencial
- Índices para melhor performance
- Views para consultas complexas
- Dados iniciais (departamentos e usuário admin)
- Charset UTF-8 para suporte completo a caracteres especiais

Usuário administrador padrão:
- Username: admin
- Senha: admin123
- Nível: admin

IMPORTANTE: Altere a senha do administrador após a primeira configuração!
*/ 