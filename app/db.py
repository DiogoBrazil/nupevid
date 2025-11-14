"""
Gerenciamento de conexão com o banco de dados PostgreSQL usando SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from app.config import Config

# Engine do SQLAlchemy
engine = create_engine(
    Config.DATABASE_URL,
    echo=Config.DEBUG,
    pool_pre_ping=True,  # Verifica conexão antes de usar
    poolclass=NullPool if Config.DEBUG else None  # No pooling em debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Thread-safe session
ScopedSession = scoped_session(SessionLocal)


class Database:
    """Classe para gerenciar conexões com PostgreSQL"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    @contextmanager
    def get_session(self):
        """Context manager para sessão do SQLAlchemy"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @contextmanager
    def get_scoped_session(self):
        """Context manager para sessão scoped (thread-safe)"""
        session = ScopedSession()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            ScopedSession.remove()


# Instância global do banco
db = Database()


def get_db():
    """Dependency injection para obter sessão do banco"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()