def main():
    print("Hello from booksmanager!")

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from uuid import uuid4
from datetime import datetime

from database import get_conn, init_db
from models import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Book's Manager", version="2.0.0", lifespan=lifespan)

# ═══════════════════ HELPERS ═══════════════════

def encontrar_usuario(id: str) -> Usuario:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id_usuario, nome, email FROM usuarios WHERE id = ?", (id, )
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return Usuario (
        id=row["id_usuario"],
        nome=row["nome"],
        email=row["email"],
    )

def encontrar_livro(id: str) -> Livro:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id_livro, titulo, autor, numero_paginas, genero, classificacao FROM livros WHERE id = ?", (id, )
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return Usuario (
        id=row["id_livro"],
        titulo=row["titulo"],
        autor=row["autor"],
        numeroPaginas=row["numero_paginas"],
        genero=row["genero"],
        classificacao=row["classificacao"],
    )

# ═══════════════════ Usuário - cadastro, edição e mais ═══════════════════

@app.get("/")
def raiz():
    return {"mensagem": "Gerenciador de Livros funcionando! 😊💕"}

@app.post("/usuarios", response_model=Usuario, status_code=201)
def criar_usuario(dados: UsuarioEntrada):
    id_usuario = str(uuid4())
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO usuarios (id_usuario, nome, email, senha) VALUES (?, ?, ?)
            """,
            (id_usuario, dados.nome, dados.email, dados.senha)
        ).fetchone()
        conn.commit()

    return Usuario(
        id=id_usuario,
        nome=dados.nome,
        email=dados.email
    )

@app.get("/usuarios", response_model=List[Usuario])
def listar_usuarios():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT nome, email, id_usuario FROM usuarios
            """
    ).fetchall()
        
        if rows is None:
            raise HTTPException(status_code=404, detail="Nenhum usuário cadastrado")

    return[
        Usuario (
            id=row["id_usuario"],
            nome=row["nome"],
            email=row["email"],
        )
        for row in rows
    ]

@app.get("/usuarios/{id}", response_model=Usuario)
def buscar_usuario(id: str):
    return encontrar_usuario(id)

@app.put("/usuarios/{id}", response_model=Usuario)
def editar_usuario(id: str, dados: UsuarioEntrada):
    with get_conn() as conn:
        cursor = conn.execute(
            """
            UPDATE usuarios SET nome = ?, email = ?, senha = ? WHERE id_usuario = ?
            """,
            (dados.nome, dados.email, dados.senha, id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    return Usuario(
        id=id,
        nome=dados.nome,
        email=dados.email
    )
        
@app.delete("/usuarios/{id}", status_code=204)
def remover_usuario(id: str):
    with get_conn() as conn:
        cursor = conn.execute(
            """
            DELETE FROM usuarios WHERE id = ?
            """,
            (id, )
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario não encontrado")
        
    return None

# ═══════════════════ Livros - criar e vincular a estante, editar e outras funções ═══════════════════

@app.post("/livros", response_model=Livro, status_code=201)
def criar_livro(dados: LivroEntrada):
    id_livro = str(uuid4())
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO livros (id_livro, titulo, autor, numero_paginas, genero) VALUES (?, ?, ?, ?, ?);
            """,
            (id_livro, dados.titulo, dados.autor, dados.numeroPaginas, dados.genero)
        )
        conn.commit()
    
    return Livro(
        id=id_livro,
        titulo=dados.titulo,
        autor=dados.autor,
        numeroPaginas=dados.numeroPaginas,
        genero=dados.genero,
    )

@app.post("/usuarios/{usuario_id}/livros/{livro_id}")
def vincular_livro(usuario_id:str, livro_id:str, dados:VinculoLivro):
    id_usuariolivro = str(uuid4())
    with get_conn() as conn:
        verifica_livro = conn.execute(
            """
            SELECT 1 FROM livros WHERE id_livro = ?
            """,
            (livro_id, )
        ).fetchone()

        if not verifica_livro:
            raise HTTPException(status_code=404, detail="Livro não encontrado")
        
        verifica_user = conn.execute(
            """
            SELECT 1 FROM usuarios WHERE id_usuario = ?
            """,
            (usuario_id, )
            ).fetchone()
        
        if not verifica_user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        conn.execute(
        """
        INSERT INTO usuariolivro (id_usuariolivro, id_usuario, id_livro, classificacao, resenha, avaliacao)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (id_usuariolivro, usuario_id, livro_id, dados.classificacao, dados.resenha, dados.nota)
    )
    conn.commit()

    return {"Mensagem: Livro vinculado com sucesso!"}

@app.get("/livros", response_model=List[Livro])
def listar_livros():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM livros
            """
        ).fetchall()

    return [
        Livro(
            id=row["id_livro"],
            titulo=row["titulo"],
            autor=row["autor"],
            numeroPaginas=row["numero_paginas"],
            genero=row["genero"]
        )
        for row in rows
    ]

@app.get("/livros/{id_livro}", response_model=Livro)
def buscar_livro(id_livro: str):
    return encontrar_livro(id_livro)

@app.put("/livros/{id_livro}", response_model=Livro)
def editar_livro(id_livro: str, dados: LivroEntrada):
    with get_conn() as conn:
        cursor = conn.execute(
            """
            UPDATE livros SET titulo = ?, autor = ?, numero_paginas = ?, genero = ? WHERE id_livro = ?
            """,
            (dados.titulo, dados.autor, dados.numeroPaginas, dados.genero, id_livro)
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Livro não encontrado")
        
        return Livro(
            id=id_livro,
            titulo=dados.titulo,
            autor=dados.autor,
            numeroPaginas=dados.numeroPaginas,
            genero=dados.genero,
        )

@app.delete("/livros/{id_livro}", status_code=204)
def remover_livro(id_livro: str):
    with get_conn() as conn:
        cursor = conn.execute(
            """
            DELETE FROM livros WHERE id_livro = ?
            """,
            (id_livro, )
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Livro não encontrado")


# ═══════════════════  Progresso e avaliação da estante ═════════════════


@app.post ("/livros/{id_livro}/historico", response_model = ProgressoLivro, status_code=201)
def registrar_progresso(id_usuariolivro:str, dados: ProgressoLivroEntrada):
    id_progresso = str(uuid4())
    data = datetime.today().date()

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO progresso (id_progresso, numero_paginas_lidas, comentario, data, id_usuariolivro)
            """,
            (id_progresso, dados.paginas_lidas, dados.comentario, data, id_usuariolivro)
            )
        conn.commit()

    return ProgressoLivro(
        id=id_progresso,
        paginas_lidas=dados.paginas_lidas,
        comentario=dados.comentario,
        data=data,
        id_usuariolivro=id_usuariolivro
    )

@app.patch("/usuarios/estante/{id_usuariolivro}/avaliar", status_code=200)
def avaliar_livro(id_usuariolivro: str, dados: AvaliacaoEntrada):
    with get_conn() as conn:
        cursor = conn.execute(
            """
            UPDATE usuariolivro SET avaliacao = ?, resenha = ? WHERE id_usuariolivro = ?
            """,
            (dados.nota, dados.resenha, id_usuariolivro)
            )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Livro não encontrado na estante deste usuário.")

        return Avaliacao (
            id=id_usuariolivro,
            nota=dados.nota,
            resenha=dados.resenha
        )

# ═══════════════════  Sorteio de Leitura ═════════════════
@app.get("/usuarios/{id_usuario}/sorteio")
def sortear_livro(id_usuario: str):
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT l.id_livro, l.titulo, l.autor, l.numero_paginas, l.genero FROM livros l
            INNER JOIN usuariolivro ul ON l.id_livro = ul.id_livro
            WHERE ul.id_usuario = ? AND ul.classificacao = "Quero Ler"
            ORDER BY RANDOM()
            LIMIT 1
'           """,
            (id_usuario, )
            ).fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Nenhum livro vinculado para sorteio")

    return {
        "livro": {
            "id": row["id_livro"],
            "titulo": row["titulo"],
            "autor": row["autor"],
            "numeroPaginas": row["numero_paginas"],
            "genero": row["genero"]
        },
        "mensagem": "🎲 O dado caiu neste livro! Que tal começar a leitura?"
    }

# ═════════════ DASHBOARD  ═════════════

@app.get("/usuarios/{id_usuario}/dashboard", response_model=DashboardResponse)
def obter_dashboard(id_usuario: str):
    with get_conn() as conn:
        metrics = conn.execute(
            """
            SELECT 
                -- 1. Conta quantos livros estão marcados estritamente como 'Lido'
                COUNT(CASE WHEN ul.classificacao = 'Lido' THEN 1 END) AS total_lidos,
                
                -- 2. Conta quantos livros estão marcados estritamente como 'Lendo'
                COUNT(CASE WHEN ul.classificacao = 'Lendo' THEN 1 END) AS total_lendo,
                
                -- 3. Soma apenas o último progresso registrado de cada livro vinculado
                COALESCE(SUM(p_recente.numero_paginas_lidas), 0) AS total_paginas
            FROM usuariolivro ul
            
            -- Subconsulta que isola apenas o ÚLTIMO progresso de cada vínculo (id_usuariolivro)
            LEFT JOIN (
                SELECT p1.id_usuariolivro, p1.numero_paginas_lidas
                FROM progresso p1
                INNER JOIN (
                    SELECT id_usuariolivro, MAX(data) AS max_data
                    FROM progresso
                    GROUP BY id_usuariolivro
                ) p2 ON p1.id_usuariolivro = p2.id_usuariolivro AND p1.data = p2.max_data
            ) p_recente ON ul.id_usuariolivro = p_recente.id_usuariolivro
            
            WHERE ul.id_usuario = ?
            """,
            (id_usuario,)
        ).fetchone()

    # Se o usuário não tiver nenhuma interação ou não for encontrado, zeramos o dashboard
    if not metrics:
        return DashboardResponse(paginas_lidas=0, livros_lidos=0, livros_lendo=0, porcentagem_concluidos=0.0)

    lidos = metrics["total_lidos"]
    lendo = metrics["total_lendo"]
    total_lendo_ou_lido = lidos + lendo

    # 4. Cálculo matemático da porcentagem evitando divisão por zero
    porcentagem = 0.0
    if total_lendo_ou_lido > 0:
        porcentagem = round((lidos / total_lendo_ou_lido) * 100, 2)


    return DashboardResponse(
        paginas_lidas=metrics["total_paginas"],
        livros_lidos=lidos,
        livros_lendo=lendo,
        porcentagem_concluidos=porcentagem
    )