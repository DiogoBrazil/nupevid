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

    # ------------------------------------------------------------------
    # Criação
    # ------------------------------------------------------------------
    @staticmethod
    def create_user(full_name, registration, email, password, rank, username=None, role: str = 'common'):
        """Cria um novo usuário (policial).

        - `username` é opcional; se não informado, usa a matrícula.
        - `role` deve ser `admin` ou `common`.
        """
        # Validações básicas
        valid_reg, msg_reg = validate_registration(registration)
        if not valid_reg:
            return False, msg_reg

        valid_email, msg_email = validate_email_format(email)
        if not valid_email:
            return False, msg_email

        valid_pwd, msg_pwd = validate_password_strength(password)
        if not valid_pwd:
            return False, msg_pwd

        username = username or registration
        role = role or 'common'
        if role not in {"admin", "common"}:
            return False, "Papel de usuário inválido. Use 'admin' ou 'common'."

        # Hash da senha
        password_hash = hash_password(password)

        # Inserir no banco
        try:
            with db.get_session() as session:
                # Verifica se email, matrícula ou username já existem
                existing = session.execute(
                    select(User).where(
                        (User.email == email)
                        | (User.registration == registration)
                        | (User.username == username)
                    )
                ).scalar_one_or_none()

                if existing:
                    if existing.email == email:
                        return False, "E-mail já cadastrado"
                    if existing.registration == registration:
                        return False, "Matrícula já cadastrada"
                    if existing.username == username:
                        return False, "Nome de usuário já cadastrado"

                # Cria novo usuário
                user = User(
                    full_name=full_name,
                    username=username,
                    registration=registration,
                    email=email,
                    password_hash=password_hash,
                    rank=rank,
                    role=role,
                )

                session.add(user)
                session.flush()

                return True, str(user.id)
        except Exception as e:
            return False, f"Erro ao criar usuário: {str(e)}"

    # ------------------------------------------------------------------
    # Autenticação
    # ------------------------------------------------------------------
    @staticmethod
    def authenticate(login: str, password: str):
        """Autentica um usuário usando `username` **ou** e-mail como login."""
        try:
            with db.get_session() as session:
                user = session.execute(
                    select(User).where(
                        (User.username == login) | (User.email == login)
                    )
                ).scalar_one_or_none()

                if not user:
                    return False, "Login ou senha incorretos"

                if not user.is_active:
                    return False, "Usuário inativo"

                if not verify_password(password, user.password_hash):
                    return False, "Login ou senha incorretos"

                return True, {
                    'id': str(user.id),
                    'full_name': user.full_name,
                    'email': user.email,
                    'rank': user.rank,
                    'role': user.role,
                    'username': user.username,
                }
        except Exception as e:
            return False, f"Erro na autenticação: {str(e)}"

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------
    @staticmethod
    def get_user_by_id(user_id):
        """Busca usuário por ID (apenas ativos)."""
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
                    'username': user.username,
                    'registration': user.registration,
                    'email': user.email,
                    'rank': user.rank,
                    'role': user.role,
                    'created_at': user.created_at,
                }
        except Exception:
            return None

    @staticmethod
    def list_users(include_inactive: bool = False):
        """Lista usuários para tela de administração."""
        try:
            with db.get_session() as session:
                stmt = select(User)
                if not include_inactive:
                    stmt = stmt.where(User.is_active == True)
                stmt = stmt.order_by(User.full_name)

                users = session.execute(stmt).scalars().all()
                return [
                    {
                        'id': str(u.id),
                        'full_name': u.full_name,
                        'username': u.username,
                        'registration': u.registration,
                        'email': u.email,
                        'rank': u.rank,
                        'role': u.role,
                        'is_active': u.is_active,
                        'created_at': u.created_at,
                    }
                    for u in users
                ]
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Atualização e exclusão
    # ------------------------------------------------------------------
    @staticmethod
    def update_user(user_id, full_name, registration, email, rank, username, role: str, password: str | None = None):
        """Atualiza dados de um usuário existente.

        Se `password` for informado, a senha é redefinida.
        """
        # Validações básicas
        valid_reg, msg_reg = validate_registration(registration)
        if not valid_reg:
            return False, msg_reg

        valid_email, msg_email = validate_email_format(email)
        if not valid_email:
            return False, msg_email

        if role not in {"admin", "common"}:
            return False, "Papel de usuário inválido. Use 'admin' ou 'common'."

        if password:
            valid_pwd, msg_pwd = validate_password_strength(password)
            if not valid_pwd:
                return False, msg_pwd

        try:
            with db.get_session() as session:
                try:
                    uid = UUID(user_id) if isinstance(user_id, str) else user_id
                except Exception:
                    uid = user_id

                user = session.execute(
                    select(User).where(User.id == uid)
                ).scalar_one_or_none()

                if not user or not user.is_active:
                    return False, "Usuário não encontrado"

                # Verifica conflitos com outros usuários
                existing = session.execute(
                    select(User).where(
                        (User.id != uid)
                        & (
                            (User.email == email)
                            | (User.registration == registration)
                            | (User.username == username)
                        )
                    )
                ).scalar_one_or_none()

                if existing:
                    if existing.email == email:
                        return False, "E-mail já cadastrado"
                    if existing.registration == registration:
                        return False, "Matrícula já cadastrada"
                    if existing.username == username:
                        return False, "Nome de usuário já cadastrado"

                # Atualiza campos
                user.full_name = full_name
                user.username = username
                user.registration = registration
                user.email = email
                user.rank = rank
                user.role = role

                if password:
                    user.password_hash = hash_password(password)

                session.flush()
                return True, str(user.id)
        except Exception as e:
            return False, f"Erro ao atualizar usuário: {str(e)}"

    @staticmethod
    def delete_user(user_id, hard_delete: bool = False):
        """Remove um usuário.

        - Por padrão faz *soft delete* (`is_active = False`).
        - Se `hard_delete=True`, remove o registro definitivamente.
        """
        try:
            with db.get_session() as session:
                try:
                    uid = UUID(user_id) if isinstance(user_id, str) else user_id
                except Exception:
                    uid = user_id

                user = session.execute(
                    select(User).where(User.id == uid)
                ).scalar_one_or_none()

                if not user:
                    return False, "Usuário não encontrado"

                if hard_delete:
                    session.delete(user)
                else:
                    user.is_active = False

                session.flush()
                return True, "Usuário removido com sucesso"
        except Exception as e:
            return False, f"Erro ao remover usuário: {str(e)}"
