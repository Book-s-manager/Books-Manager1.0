def main():
    print("Hello from booksmanager!")

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends

from uuid import uuid4
from datetime import datetime

from database import *
from models import *

from security import verificar_api_key

from sqlalchemy.orm import Session

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Book's Manager", version="2.0.0", lifespan=lifespan)

# ═══════════════════ HELPERS ═══════════════════

def encontrar_usuario(id: str, db: Session) -> UsuarioDB:
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id_usuario == id).first()

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return usuario

def encontrar_livro(id: str, db: Session) -> LivroDB:
    livro = db.query(LivroDB).filter(LivroDB.id_livro == id).first()

    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    return livro

# ═══════════════════ Usuário - cadastro, edição e mais ═══════════════════

@app.get("/")
def raiz():
    return {"mensagem": "Gerenciador de Livros funcionando! 😊💕"}

@app.post("/usuarios", response_model=Usuario, status_code=201)
def criar_usuario(dados: UsuarioEntrada, db: Session = Depends(get_db)):
    id_usuario = str(uuid4())

    novo_usuario = UsuarioDB(
        id_usuario=id_usuario,
        nome=dados.nome,
        email=dados.email,
        senha=dados.senha
    )

    try:
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar usuário")
    
    return Usuario(
        id=id_usuario,
        nome=dados.nome,
        email=dados.email,
    )

@app.get("/usuarios", response_model=List[Usuario])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(UsuarioDB).all()

    if not usuarios:
        raise HTTPException(status_code=404, detail="Nenhum usuário encontrado")
    
    return usuarios

@app.get("/usuarios/{id}", response_model=Usuario)
def buscar_usuario(id: str, db: Session = Depends(get_db)):
    return encontrar_usuario(id)

@app.put("/usuarios/{id}", response_model=Usuario, dependencies=[Depends(verificar_api_key)])
def editar_usuario(id: str, dados: UsuarioEntrada, db: Session = Depends(get_db)):
    usuario = encontrar_usuario(id, db)

    usuario.nome = dados.nome
    usuario.email = dados.email
    usuario.senha = dados.senha

    try:
        db.commit()
        db.refresh(usuario)

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao editar usuário")

    return usuario

@app.delete("/usuarios/{id}", status_code=204, dependencies=[Depends(verificar_api_key)])
def remover_usuario(id: str, db: Session = Depends(get_db)):
    usuario = encontrar_usuario(id, db)
    db.delete(usuario)

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao remover usuário")

    return None

# ═══════════════════ Livros - criar e vincular a estante, editar e outras funções ═══════════════════

@app.post("/livros", response_model=Livro, status_code=201)
def criar_livro(dados: LivroEntrada, db: Session = Depends(get_db)  ):
    id_livro = str(uuid4())

    novo_livro = LivroDB(
        id_livro=id_livro,
        titulo=dados.titulo,
        autor=dados.autor,
        numero_paginas=dados.numeroPaginas,
        genero=dados.genero
    )

    try:
        db.add(novo_livro)
        db.commit()
        db.refresh(novo_livro)

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar livro")

    return Livro(
        id=id_livro,
        titulo=dados.titulo,
        autor=dados.autor,
        numeroPaginas=dados.numeroPaginas,
        genero=dados.genero,
    )

@app.post("/usuarios/{usuario_id}/livros/{livro_id}")
def vincular_livro(usuario_id:str, livro_id:str, dados:VinculoLivro, db: Session = Depends(get_db)):
    id_usuariolivro = str(uuid4())

    encontrar_usuario(usuario_id, db)
    encontrar_livro(livro_id, db)
        
    resenha_limpa = dados.resenha if dados.resenha and dados.resenha.strip() != "" else None
    nota_limpa = dados.nota if dados.nota is not None and 1 <= dados.nota <= 5 else None

    novo_vinculo = UsuarioLivroDB(
        id_usuariolivro=id_usuariolivro,
        id_usuario=usuario_id,
        id_livro=livro_id,
        classificacao=dados.classificacao,
        resenha=resenha_limpa,
        avaliacao=nota_limpa
    )

    try:
        db.add(novo_vinculo)
        db.commit()
        db.refresh(novo_vinculo)

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao vincular livro à estante do usuário")

    return {"Mensagem": "Livro vinculado com sucesso!"}

@app.get("/livros", response_model=List[Livro])
def listar_livros(db: Session = Depends(get_db)):
    usuarios = db.query(UsuarioDB).all()

    if not usuarios:
        raise HTTPException(status_code=404, detail="Nenhum usuário encontrado")
    
    return usuarios

@app.get("/livros/{id_livro}", response_model=Livro)
def buscar_livro(id_livro: str, db: Session = Depends(get_db)):
    return encontrar_livro(id_livro, db)

@app.put("/livros/{id_livro}", response_model=Livro, dependencies=[Depends(verificar_api_key)])
def editar_livro(id_livro: str, dados: LivroEntrada, db: Session = Depends(get_db)):
    livro = encontrar_livro(id_livro, db)

    livro.titulo = dados.titulo
    livro.autor = dados.autor
    livro.numero_paginas = dados.numeroPaginas
    livro.genero = dados.genero

    try:
        db.commit()
        db.refresh(livro)

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao editar livro")

    return livro

@app.delete("/livros/{id_livro}", status_code=204, dependencies=[Depends(verificar_api_key)])
def remover_livro(id_livro: str, db: Session = Depends(get_db)):
    livro = encontrar_livro(id_livro, db)
    db.delete(livro)

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao remover livro")

    return None

# ═══════════════════  Progresso e avaliação da estante ═════════════════
@app.get("/usuarios/{id_usuario}/estante", response_model=List[Estante])
def exibir_estante(id_usuario, db: Session = Depends(get_db)):
    encontrar_usuario(id_usuario, db)

    itens_estante = db.query(UsuarioLivroDB).filter(UsuarioLivroDB.id_usuario == id_usuario).all()

    resposta = []
    for item in itens_estante:
        resposta.append({
            "id": item.id_usuariolivro,
            "id_livro": item.id_livro,
            "titulo": item.livro.titulo,
            "autor": item.livro.autor,
            "numeroPaginas": item.livro.numero_paginas,
            "genero": item.livro.genero,
            "classificacao": item.classificacao,
            "nota": item.avaliacao,
            "resenha": item.resenha
        })

@app.post ("/livros/{id_livro}/historico", response_model = ProgressoLivro, status_code=201)
def registrar_progresso(id_usuariolivro:str, dados: ProgressoLivroEntrada, db: Session = Depends(get_db)):
    id_progresso = str(uuid4())
    data = datetime.today().date()

    novo_progresso = ProgressoDB(
        id_progresso=id_progresso,
        numero_paginas_lidas=dados.paginas_lidas,
        comentario=dados.comentario,
        data=data,
        id_usuariolivro=id_usuariolivro
    )

    try:
        db.add(novo_progresso)
        db.commit()
        db.refresh(novo_progresso)

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao registrar progresso do livro")

    return ProgressoLivro(
        id=id_progresso,
        paginas_lidas=dados.paginas_lidas,
        comentario=dados.comentario,
        data=data,
        id_usuariolivro=id_usuariolivro
    )

@app.get("/usuarios/{id_usuario}/historicos", response_model=List[HistoricoProgressoResponse])
def ver_progressos(id_usuario: str, db: Session = Depends(get_db)):
    encontrar_usuario(id_usuario, db)
    
    rows = (
        db.query(ProgressoDB)
        .join(UsuarioLivroDB, ProgressoDB.id_usuariolivro == UsuarioLivroDB.id_usuariolivro)
        .join(LivroDB, UsuarioLivroDB.id_livro == LivroDB.id_livro)
        .filter(UsuarioLivroDB.id_usuario == id_usuario)
        .order_by(ProgressoDB.data.desc())
        .all()
    )
    
    resultado = []
    for p in rows:
        resultado.append({
            "id_progresso": p.id_progresso,
            "id_livro": p.vinculo_estante.id_livro,
            # 🌟 Mágica do ORM: navegando do progresso até o livro vinculado!
            "titulo_livro": p.vinculo_estante.livro.titulo,
            "autor_livro": p.vinculo_estante.livro.autor,
            "numero_paginas_lidas": p.numero_paginas_lidas,
            "comentario": p.comentario,
            "data": p.data
        })
        
    return resultado

@app.patch("/usuarios/estante/{id_usuariolivro}/avaliar", status_code=200)
def avaliar_livro(id_usuariolivro: str, dados: AvaliacaoEntrada, db: Session = Depends(get_db)):
    vinculo_banco = db.query(UsuarioLivroDB).filter(UsuarioLivroDB.id_usuariolivro == id_usuariolivro).first()

    if not vinculo_banco:
        raise HTTPException(status_code=404, detail="Livro não encontrado na estante deste usuário.")
        
    vinculo_banco.avaliacao = dados.nota
    vinculo_banco.resenha = dados.resenha
    
    try:
        db.commit()
        db.refresh(vinculo_banco)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao salvar a avaliação. Verifique as restrições de nota (1 a 5).")

    return Avaliacao(
        id=vinculo_banco.id_usuariolivro,
        nota=vinculo_banco.avaliacao,
        resenha=vinculo_banco.resenha
    )

# ═══════════════════  Sorteio de Leitura ═════════════════
@app.get("/usuarios/{id_usuario}/sorteio")
def sortear_livro(id_usuario: str, db: Session = Depends(get_db)):
    encontrar_usuario(id_usuario, db)
    
    registro_sorteado = (
        db.query(LivroDB)
        .join(UsuarioLivroDB, LivroDB.id_livro == UsuarioLivroDB.id_livro)
        .filter(UsuarioLivroDB.id_usuario == id_usuario)
        .filter(UsuarioLivroDB.classificacao == "Quero Ler")
        .order_by(func.random())
        .first()
    )

    if not registro_sorteado:
        raise HTTPException(status_code=404, detail="Nenhum livro vinculado para sorteio")

    return {
        "livro": {
            "id": registro_sorteado.id_livro,
            "titulo": registro_sorteado.titulo,
            "autor": registro_sorteado.autor,
            "numeroPaginas": registro_sorteado.numero_paginas,
            "genero": registro_sorteado.genero
        },
        "mensagem": "🎲 O dado caiu neste livro! Que tal começar a leitura?"
    }

# ═════════════ DASHBOARD  ═════════════
@app.get("/usuarios/{id_usuario}/dashboard", response_model=DashboardResponse)
def obter_dashboard(id_usuario: str, db: Session = Depends(get_db)):
    # 1. Valida se o usuário existe usando o helper comum
    encontrar_usuario(id_usuario, db)

    # 2. Query 1: Contar quantos livros estão como 'Lido' e quantos estão como 'Lendo'
    # Fazemos isso em uma única consulta rápida no banco
    metricas_livros = (
        db.query(
            func.count(func.distinct(func.case((UsuarioLivroDB.classificacao == 'Lido', UsuarioLivroDB.id_usuariolivro)))),
            func.count(func.distinct(func.case((UsuarioLivroDB.classificacao == 'Lendo', UsuarioLivroDB.id_usuariolivro))))
        )
        .filter(UsuarioLivroDB.id_usuario == id_usuario)
        .first()
    )
    
    total_lidos = metricas_livros[0] or 0
    total_lendo = metricas_livros[1] or 0

    total_paginas = (
        db.query(func.sum(ProgressoDB.numero_paginas_lidas))
        .join(UsuarioLivroDB, ProgressoDB.id_usuariolivro == UsuarioLivroDB.id_usuariolivro)
        .filter(UsuarioLivroDB.id_usuario == id_usuario)
        .scalar()
    ) or 0

    total_lendo_ou_lido = total_lidos + total_lendo
    porcentagem = 0.0
    if total_lendo_ou_lido > 0:
        porcentagem = round((total_lidos / total_lendo_ou_lido) * 100, 2)

    return DashboardResponse(
        paginas_lidas=total_paginas,
        livros_lidos=total_lidos,
        livros_lendo=total_lendo,
        porcentagem_concluidos=porcentagem
    )