import sqlite3

# Caminho do arquivo do banco de dados
DB_PATH = "books_manager.db"

def get_conn() -> sqlite3.Connection:
    """Abre e retorna uma conexão com o banco."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON") #ATIVAR CHAVES ESTRANGEIRAS
    # Permite acessar colunas pelo nome: row["titulo"]
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Cria a tabela se ela ainda não existir."""
    with get_conn() as conn:
        conn.executescript("""
                           
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario  TEXT PRIMARY KEY,
                nome    TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha VARCHAR(250) NOT NULL
            );
                     
            CREATE TABLE IF NOT EXISTS livros (
                id_livro TEXT PRIMARY KEY,
                titulo VARCHAR (150) NOT NULL,
                autor VARCHAR(150) NOT NULL,
                numero_paginas INTEGER NOT NULL,
                genero  VARCHAR(150) NOT NULL
                           
            );
                           
            CREATE TABLE IF NOT EXISTS usuariolivro (
                id_usuariolivro TEXT PRIMARY KEY,
                id_usuario TEXT NOT NULL,
                id_livro TEXT NOT NULL,
                classificacao TEXT NOT NULL CHECK (classificacao IN ('Quero Ler', 'Lendo', 'Lido')),
                resenha VARCHAR(300),
                avaliacao INTEGER CHECK (avaliacao BETWEEN 1 AND 5),
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario),
                FOREIGN KEY(id_livro) REFERENCES livros(id_livro),
                UNIQUE(id_usuario, id_livro)
            );
                           
            CREATE TABLE IF NOT EXISTS progresso (
                id_progresso TEXT PRIMARY KEY,
                numero_paginas_lidas INTEGER NOT NULL CHECK(numero_paginas_lidas >= 0),
                comentario VARCHAR(300),
                data DATETIME DEFAULT CURRENT_TIMESTAMP,
                id_usuariolivro TEXT NOT NULL,
                FOREIGN KEY(id_usuariolivro) REFERENCES usuariolivro(id_usuariolivro)
            )
                           
        """)
        conn.commit()