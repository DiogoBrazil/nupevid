"""
Model de vítima usando UUID como PK
"""
import uuid
from sqlalchemy import Column, String, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class Victim(Base, TimestampMixin):
    """Modelo de vítima"""
    
    __tablename__ = 'victims'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    cpf = Column(String(14), nullable=True, unique=True)
    phone = Column(String(50), nullable=True)
    secondary_phone = Column(String(50), nullable=True)
    
    # Endereço
    address_type = Column(String(50), nullable=True)
    address_name = Column(String(255), nullable=True)
    address_number = Column(String(20), nullable=True)
    address_complement = Column(String(255), nullable=True)
    neighborhood = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)
    
    __table_args__ = (
        CheckConstraint(
            "state ~ '^[A-Z]{2}$' OR state IS NULL",
            name='chk_state'
        ),
    )
    
    def __repr__(self):
        return f"<Victim(id={self.id}, name='{self.full_name}')>"