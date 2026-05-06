def main():
    print("Hello from booksmanager!")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI(title="Book's Manager", version="1.0.0")

# ═══════════════════ MODELOS ═══════════════════



class LivroEntrada(BaseModel):
    titulo: str
    autor: str
    numeroPaginas: int
    genero: str
    classificacao: str

class Livro(LivroEntrada):
    id: str
    nota: Optional[int] = None
    resenha: Optional[str] = None

class ProgressoLivroEntrada(BaseModel):
    comentario:str
    paginas_lidas: int

class ProgressoLivro(ProgressoLivroEntrada):
    id: str
    data: datetime =datetime.now()
    livro_id: str

class UsuarioEntrada(BaseModel):
    nome: str
    email: str
    senha: str

class Usuario(UsuarioEntrada):
    id: str
    estantePessoal: List[Livro] = []

class AvaliacaoEntrada(BaseModel):
    nota: int
    resenha: str

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

# ═══════════════════ Usuário - cadastro e gerenciamento ═══════════════════

@app.get("/")
def raiz():
    return {"mensagem": "Gerenciador de Livros funcionando! 😊💕"}

@app.post("/usuario", response_model=Usuario, status_code=201)
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

# ═══════════════════ Livros - criar, vincular a estante, editar e outras funções ═══════════════════

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

# ═══════════════════ MATRÍCULAS ═══════════════════

# @app.post("/matriculas", response_model=Matricula, status_code=201)
# def matricular_aluno(dados: MatriculaEntrada):
#     encontrar_aluno(dados.aluno_id)
#     encontrar_disciplina(dados.disciplina_id)
#     for m in matriculas_db:
#         if m.aluno_id == dados.aluno_id and m.disciplina_id == dados.disciplina_id:
#             raise HTTPException(status_code=409, detail="Aluno já matriculado nesta disciplina")
#     nova = Matricula(id=str(uuid.uuid4()), **dados.model_dump())
#     matriculas_db.append(nova)
#     return nova

# @app.get("/alunos/{id}/disciplinas", response_model=List[Disciplina])
# def disciplinas_do_aluno(id: str):
#     encontrar_aluno(id)
#     ids_disc = {m.disciplina_id for m in matriculas_db if m.aluno_id == id}
#     return [d for d in disciplinas_db if d.id in ids_disc]

# @app.get("/disciplinas/{id}/alunos", response_model=List[Aluno])
# def alunos_da_disciplina(id: str):
#     encontrar_disciplina(id)
#     ids_alunos = {m.aluno_id for m in matriculas_db if m.disciplina_id == id}
#     return [a for a in alunos_db if a.id in ids_alunos]

# @app.delete("/matriculas/{id}", status_code=204)
# def cancelar_matricula(id: str):
#     for i, m in enumerate(matriculas_db):
#         if m.id == id:
#             matriculas_db.pop(i)
#             return
#     raise HTTPException(status_code=404, detail="Matrícula não encontrada")

# # ═══════════════════ INFRAÇÕES ═══════════════════

# @app.post("/infracoes", response_model=Infracao, status_code=201)
# def registrar_infracao(dados: InfracaoEntrada):
#     encontrar_aluno(dados.aluno_id)
#     encontrar_disciplina(dados.disciplina_id)
#     nova = Infracao(
#         id=str(uuid.uuid4()),
#         data=datetime.now().isoformat(),
#         **dados.model_dump()
#     )
#     infracoes_db.append(nova)
#     return nova

# @app.get("/infracoes", response_model=List[Infracao])
# def listar_infracoes():
#     return infracoes_db

# @app.get("/infracoes/{id}", response_model=Infracao)
# def buscar_infracao(id: str):
#     for inf in infracoes_db:
#         if inf.id == id:
#             return inf
#     raise HTTPException(status_code=404, detail="Infração não encontrada")

# @app.get("/alunos/{id}/infracoes", response_model=List[Infracao])
# def infracoes_do_aluno(id: str):
#     encontrar_aluno(id)
#     return [inf for inf in infracoes_db if inf.aluno_id == id]

# @app.get("/disciplinas/{id}/infracoes", response_model=List[Infracao])
# def infracoes_da_disciplina(id: str):
#     encontrar_disciplina(id)
#     return [inf for inf in infracoes_db if inf.disciplina_id == id]

# @app.put("/infracoes/{id}", response_model=Infracao)
# def editar_infracao(id: str, dados: InfracaoEntrada):
#     for i, inf in enumerate(infracoes_db):
#         if inf.id == id:
#             atualizada = Infracao(id=id, data=inf.data, **dados.model_dump())
#             infracoes_db[i] = atualizada
#             return atualizada
#     raise HTTPException(status_code=404, detail="Infração não encontrada")

# @app.delete("/infracoes/{id}", status_code=204)
# def remover_infracao(id: str):
#     for i, inf in enumerate(infracoes_db):
#         if inf.id == id:
#             infracoes_db.pop(i)
#             return
#     raise HTTPException(status_code=404, detail="Infração não encontrada")