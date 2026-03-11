USE kallirp;
 
-- ─── TABELA: users ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    username         VARCHAR(50) NOT NULL UNIQUE,
    password_hash    VARCHAR(255) NOT NULL,
    display_name     VARCHAR(100),
    role             ENUM('staff','chefe','admin') NOT NULL DEFAULT 'staff',
    hierarquia_nivel INT NOT NULL DEFAULT 1,
    ativo            BOOLEAN NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login       TIMESTAMP NULL
);
 
-- ─── TABELA: gestoes ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gestoes (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    slug VARCHAR(50)  NOT NULL UNIQUE
);
 
-- ─── TABELA: gestao_membros ───────────────────────────────────
-- Um staff pode estar em múltiplas gestões (ex: Costa está em
-- Gestão de POVs e Gestão de Conteúdos)
CREATE TABLE IF NOT EXISTS gestao_membros (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    gestao_id  INT NOT NULL,
    is_chefe   BOOLEAN NOT NULL DEFAULT FALSE,
    joined_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
    FOREIGN KEY (gestao_id) REFERENCES gestoes(id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_gestao (user_id, gestao_id)
);
 
-- ─── TABELA: criterios_avaliacao ──────────────────────────────
CREATE TABLE IF NOT EXISTS criterios_avaliacao (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    descricao  TEXT,
    gestao_id  INT NULL,
    ativo      BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (gestao_id) REFERENCES gestoes(id) ON DELETE SET NULL
);
 
-- ─── TABELA: avaliacoes ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS avaliacoes (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    avaliador_id  INT NOT NULL,
    avaliado_id   INT NOT NULL,
    gestao_id     INT NOT NULL,
    nota_final    DECIMAL(4,2) NOT NULL CHECK (nota_final BETWEEN 0 AND 20),
    comentario    TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (avaliador_id) REFERENCES users(id),
    FOREIGN KEY (avaliado_id)  REFERENCES users(id),
    FOREIGN KEY (gestao_id)    REFERENCES gestoes(id)
);
 
-- ─── TABELA: notas_criterios ──────────────────────────────────
-- Cada critério individual de uma avaliação
CREATE TABLE IF NOT EXISTS notas_criterios (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    avaliacao_id   INT NOT NULL,
    criterio_id    INT NOT NULL,
    nota           DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes(id) ON DELETE CASCADE,
    FOREIGN KEY (criterio_id)  REFERENCES criterios_avaliacao(id)
);
 
-- ─── TABELA: inbox ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inbox (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    destinatario_id   INT NOT NULL,
    remetente_id      INT NULL,
    tipo              ENUM('avaliacao','hierarquia','sistema') NOT NULL,
    titulo            VARCHAR(200) NOT NULL,
    conteudo          TEXT NOT NULL,
    avaliacao_id      INT NULL,
    lida              BOOLEAN NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (destinatario_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (remetente_id)    REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (avaliacao_id)    REFERENCES avaliacoes(id) ON DELETE SET NULL
);
 
-- ─── TABELA: reports_tickets ──────────────────────────────────
CREATE TABLE IF NOT EXISTS reports_tickets (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    tipo          ENUM('report','ticket') NOT NULL,
    quantidade    INT NOT NULL DEFAULT 0,
    periodo       DATE NOT NULL,
    importado_em  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
 
-- ─── TABELA: historico_hierarquia ─────────────────────────────
CREATE TABLE IF NOT EXISTS historico_hierarquia (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    autor_id        INT NOT NULL,
    nivel_antes     INT NOT NULL,
    nivel_depois    INT NOT NULL,
    justificacao    TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)  REFERENCES users(id),
    FOREIGN KEY (autor_id) REFERENCES users(id)
);
 
-- ─── TABELA: audit_log ────────────────────────────────────────
-- Regista todas as ações importantes do sistema
CREATE TABLE IF NOT EXISTS audit_log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NULL,
    acao        VARCHAR(100) NOT NULL,
    detalhes    TEXT,
    ip          VARCHAR(45),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
