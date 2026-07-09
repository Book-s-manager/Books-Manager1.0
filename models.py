from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
# ═══════════════════ MODELOS ═══════════════════

class LivroEntrada(BaseModel):
    titulo: str
    autor: str
    numeroPaginas: int
    genero: str

class Livro(LivroEntrada):
    id: str
    nota: Optional[int] = None
    resenha: Optional[str] = None

class VinculoLivro(LivroEntrada):
    classificacao: str
    nota: Optional[int] = None
    resenha: Optional[str] = None

class ProgressoLivroEntrada(BaseModel):
    comentario:str
    paginas_lidas: int

class ProgressoLivro(ProgressoLivroEntrada):
    id: str
    data: datetime =datetime.now()
    id_usuariolivro: str

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

class Avaliacao(AvaliacaoEntrada):
    id: str

class DashboardResponse(BaseModel):
    paginas_lidas: int
    livros_lidos: int
    livros_lendo: int
    porcentagem_concluidos: float