import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, CheckConstraint, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
# ================ MÉTODO NOVO (SQLALCHEMY) ================

SQLALCHEMY_DATABASE_URL = "sqlite:///./books_manager.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)         

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        db.execute("PRAGMA foreign_keys = ON")
        yield db
    finally:
        db.close()

class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(String, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    senha = Column(String, nullable=False)

    livros_estante = relationship("UsuarioLivroDB", back_populates="usuario", cascade="all, delete-orphan")

class LivroDB(Base):
    __tablename__ = "livros"

    id_livro = Column(String, primary_key=True)
    titulo = Column(String, nullable=False)
    numero_paginas = Column(Integer, nullable=False)
    genero = Column(String, nullable=False)

    usuarios_que_adicionaram = relationship("UsuarioLivroDB", back_populates="livro", cascade="all, delete-orphan")

class UsuarioLivroDB(Base):
    __tablename__ = "usuariolivro"

    id_usuariolivro = Column(String, primary_key=True)
    id_usuario = Column(String, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_livro = Column(String, ForeignKey("livros.id_livro"), nullable=False)
    classificacao = Column(String, nullable=False)
    resenha = Column(String)
    avaliacao = Column(Integer)

    usuario = relationship("UsuarioDB", back_populates="livros_estante")
    livro = relationship("LivroDB", back_populates="usuarios_que_adicionaram")

    progressos = relationship("ProgressoDB", back_populates="vinculo_estante", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(classificacao.in_(['Quero Ler', 'Lendo', 'Lido']), name='check_classificacao'),
        CheckConstraint('avaliacao >= 1 AND avaliacao <= 5', name='check_avaliacao'),
    )

class ProgressoDB(Base):
    __tablename__ = "progresso"

    id_progresso = Column(String, primary_key=True)
    numero_paginas_lidas = Column(Integer, nullable=False)
    comentario = Column(String)
    data = Column(DateTime, default=func.now())
    id_usuariolivro = Column(String, ForeignKey("usuariolivro.id_usuariolivro"), nullable=False)

    vinculo_estante = relationship("UsuarioLivroDB", back_populates="progresso")    