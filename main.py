def main():
    print("Hello from booksmanager!")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import random
from contextlib import asynccontextmanager
from models import *

from database import get_conn, init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executado na inicialização: cria tabelas se não existirem
    init_db()
    yield
    # Executado no encerramento (se necessário)


app = FastAPI(title="Book's Manager", version="2.0.0", lifespan="lifespan")


# ═══════════════════ DADOS EM MEMÓRIA ═══════════════════

usuarios_db: List[Usuario] = []
livros_db: List[Livro] = []
progressoLivro_db: List[ProgressoLivro] = []

# ═══════════════════ HELPERS ═══════════════════

def encontrar_usuario(id: str) -> Usuario:
    for a in usuarios_db:
        if a.id == id:
            return a
    raise HTTPException(status_code=404, detail="Usuário não encontrado")

def encontrar_livro(id: str) -> Livro:
    for l in livros_db:
        if l.id == id:
            return l
    raise HTTPException(status_code=404, detail="Livro não encontrado")

# ═══════════════════ Usuário - cadastro, edição e mais ═══════════════════

@app.get("/")
def raiz():
    return {"mensagem": "Gerenciador de Livros funcionando! 😊💕"}

@app.post("/usuarios", response_model=Usuario, status_code=201)
def criar_usuario(dados: UsuarioEntrada):
    novo = Usuario(id=str(uuid.uuid4()), estantePessoal=[], **dados.model_dump())
    usuarios_db.append(novo)
    return novo

@app.get("/usuarios", response_model=List[Usuario])
def listar_usuarios():
    return usuarios_db

@app.get("/usuarios/{id}", response_model=Usuario)
def buscar_usuario(id: str):
    return encontrar_usuario(id)

@app.put("/usuarios/{id}", response_model=Usuario)
def editar_usuario(id: str, dados: UsuarioEntrada):
    for i, a in enumerate(usuarios_db): 
        if a.id == id:
            atualizado = Usuario(id=id, **dados.model_dump())
            usuarios_db[i] = atualizado
            return atualizado
    raise HTTPException(status_code=404, detail="Usuario não encontrado")

@app.delete("/usuarios/{id}", status_code=204)
def remover_usuario(id: str):
    for i, u in enumerate(usuarios_db):
        if u.id == id:
            usuarios_db.pop(i)
            return
    raise HTTPException(status_code=404, detail="Usuario não encontrado")

# ═══════════════════ Livros - criar e vincular a estante, editar e outras funções ═══════════════════

@app.post("/usuarios/{usuario_id}/livros", response_model=Livro, status_code=201)
def criar_e_vincular_livro(usuario_id: str, dados: LivroEntrada):
    novo = Livro(id=str(uuid.uuid4()), **dados.model_dump())
    livros_db.append(novo)
    usuario = encontrar_usuario(usuario_id)

    status_para_estante = ["lendo", "lido"]
    if dados.classificacao.lower() in status_para_estante:
        if usuario.estantePessoal is None:
            usuario.estantePessoal = []
        usuario.estantePessoal.append(novo)
    
    return novo


@app.get("/livros", response_model=List[Livro])
def listar_livros():
    return livros_db

@app.get("/livros/{id}", response_model=Livro)
def buscar_livro(id: str):
    return encontrar_livro(id)

@app.put("/livros/{id}", response_model=Livro)
def editar_livro(id: str, dados: LivroEntrada):
    for i, l in enumerate(livros_db):
        if l.id == id:
            atualizada = Livro(id=id, **dados.model_dump())
            livros_db[i] = atualizada
            return atualizada
    raise HTTPException(status_code=404, detail="Livro não encontrado")

@app.delete("/livros/{id}", status_code=204)
def remover_livro(id: str):
    for i, l in enumerate(livros_db):
        if l.id == id:
            livros_db.pop(i)
            return
    raise HTTPException(status_code=404, detail="Livro não encontrado")


# ═══════════════════  Progresso e avaliação da estante ═════════════════


@app.post ("/livros/{id}/historico", response_model = ProgressoLivro, status_code=201)
def registrar_progresso(id:str, dados: ProgressoLivroEntrada):
    livro= encontrar_livro(id)
    if dados.paginas_lidas > livro.numeroPaginas:
        raise HTTPException(
            status_code=400,
            detail="Páginas lidas não podem exceder o total do livro."
        )
    novo_progresso = ProgressoLivro(
        id=str(uuid.uuid4()),
        livro_id=id,
        comentario=dados.comentario,
        paginas_lidas=dados.paginas_lidas
    )
    progressoLivro_db.append(novo_progresso)
    return novo_progresso

@app.patch("/usuarios/{usuario_id}/estante/{livro_id}/avaliar", status_code=200)
def avaliar_livro(usuario_id: str, livro_id: str, dados: AvaliacaoEntrada):
    usuario = encontrar_usuario(usuario_id)
    
    if not (1 <= dados.nota <= 5):
        raise HTTPException(status_code=400, detail="A nota deve ser entre 1 e 5.")

    for livro in usuario.estantePessoal:
        if livro.id == livro_id:
            livro.nota = dados.nota
            livro.resenha = dados.resenha
            return {"mensagem": "Avaliação registrada!", "livro": livro.titulo}
        
    raise HTTPException(status_code=404, detail="Livro não encontrado na estante deste usuário.")

# ═══════════════════  Sorteio de Leitura ═════════════════

@app.get("/usuarios/{usuario_id}/sorteio")
def sortear_livro(usuario_id: str):
    usuario = encontrar_usuario(usuario_id)

    livros_sorteio = [l for l in livros_db if l.classificacao.lower() == "quero ler"]
    if not livros_sorteio:
        raise HTTPException(
            status_code=404, 
            detail="Não encontramos livros com status 'quero ler' no catálogo."
        )
    escolhido = random.choice(livros_sorteio)
    return {
        "sugestao": escolhido.titulo,
        "autor": escolhido.autor,
        "genero": escolhido.genero,
        "mensagem": "🎲 O dado caiu neste livro! Que tal começar a leitura?"
    }


# ═════════════ DASHBOARD  ═════════════


@app.get("/usuarios/{usuario_id}/dashboard")
def exibir_dashboard(usuario_id: str):
    usuario = encontrar_usuario(usuario_id)
    
    total_livros = len(usuario.estantePessoal)
    
    total_paginas = sum(livro.numeroPaginas for livro in usuario.estantePessoal)
    
    lidos = [l for l in usuario.estantePessoal if l.classificacao.lower() == "lido"]
    lendo = [l for l in usuario.estantePessoal if l.classificacao.lower() == "lendo"]

    mensagem = "Comece sua jornada de leitura! 📖"
    if total_livros > 0:
        porcentagem_concluida = (len(lidos) / total_livros) * 100
        mensagem = f"Você já concluiu {porcentagem_concluida:.1f}% da sua estante!"

    return {
        "usuario": usuario.nome,
        "estatisticas": {
            "total_na_estante": total_livros,
            "livros_concluidos": len(lidos),
            "lendo_atualmente": len(lendo),
            "paginas_totais": total_paginas
        },
        "feedback": mensagem
    }