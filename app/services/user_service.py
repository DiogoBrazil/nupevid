"""
Serviço de gerenciamento de usuários usando SQLAlchemy
"""
from sqlalchemy import select
from app.db import db
from app.models.user import User
from app.auth.utils import (
    hash_password, verify_password,
    validate_registration, validate_email_format,
    validate_password_strength
)
from uuid import UUID

class UserService:
    """Serviço para operações com usuários"""
    
    @staticmethod
    def create_user(full_name, registration, email, password, rank):
        """
        Cria um novo usuário (policial)
        """
        # Validações
        valid_reg, msg_reg = validate_registration(registration)
        if not valid_reg:
            return False, msg_reg
        
        valid_email, msg_email = validate_email_format(email)
        if not valid_email:
            return False, msg_email
        
        valid_pwd, msg_pwd = validate_password_strength(password)
        if not valid_pwd:
            return False, msg_pwd
        
        # Hash da senha
        password_hash = hash_password(password)
        
        # Inserir no banco
        try:
            with db.get_session() as session:
                # Verifica se email ou matrícula já existem
                existing = session.execute(
                    select(User).where(
                        (User.email == email) | (User.registration == registration)
                    )
                ).first()
                
                if existing:
                    if existing[0].email == email:
                        return False, "E-mail já cadastrado"
                    if existing[0].registration == registration:
                        return False, "Matrícula já cadastrada"
                
                # Cria novo usuário
                user = User(
                    full_name=full_name,
                    registration=registration,
                    email=email,
                    password_hash=password_hash,
                    rank=rank
                )
                
                session.add(user)
                session.flush()
                
                return True, str(user.id)
        except Exception as e:
            return False, f"Erro ao criar usuário: {str(e)}"
    
    @staticmethod
    def authenticate(email, password):
        """
        Autentica um usuário
        """
        try:
            with db.get_session() as session:
                user = session.execute(
                    select(User).where(User.email == email)
                ).scalar_one_or_none()
                
                if not user:
                    return False, "E-mail ou senha incorretos"
                
                if not user.is_active:
                    return False, "Usuário inativo"
                
                if not verify_password(password, user.password_hash):
                    return False, "E-mail ou senha incorretos"
                
                return True, {
                    'id': str(user.id),
                    'full_name': user.full_name,
                    'email': user.email,
                    'rank': user.rank
                }
        except Exception as e:
            return False, f"Erro na autenticação: {str(e)}"
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Busca usuário por ID
        """
        try:
            with db.get_session() as session:
                # allow user_id as str or UUID
                try:
                    uid = UUID(user_id) if isinstance(user_id, str) else user_id
                except Exception:
                    uid = user_id

                user = session.execute(
                    select(User).where(
                        (User.id == uid) & (User.is_active == True)
                    )
                ).scalar_one_or_none()
                
                if not user:
                    return None
                
                return {
                    'id': user.id,
                    'full_name': user.full_name,
                    'registration': user.registration,
                    'email': user.email,
                    'rank': user.rank,
                    'created_at': user.created_at
                }
        except Exception as e:
            return None