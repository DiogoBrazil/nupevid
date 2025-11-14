"""
Model de usuário (policial) usando UUID como PK
"""
import uuid
from sqlalchemy import Column, String, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Modelo de usuário (policial)"""
    
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    registration = Column(String(9), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    rank = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False, default='common')
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        CheckConstraint(
            "registration ~ '^1000[0-9]{5}$'",
            name='chk_registration'
        ),
        CheckConstraint(
            "rank IN ('CEL PM', 'TC PM', 'MAJ PM', 'CAP PM', "
            "'1º TEN PM', '2º TEN PM', 'ASP OF PM', 'ST PM', "
            "'1º SGT PM', '2º SGT PM', '3º SGT PM', 'CB PM', 'SD PM')",
            name='chk_rank'
        ),
        CheckConstraint(
            "role IN ('admin', 'common')",
            name='chk_role'
        ),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.full_name}', rank='{self.rank}')>"