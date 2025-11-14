"""
Model de atendimento usando UUID para chaves
"""
import uuid
from sqlalchemy import Column, String, Date, DateTime, Text, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Attendance(Base, TimestampMixin):
    """Modelo de atendimento"""
    
    __tablename__ = 'attendances'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    victim_id = Column(UUID(as_uuid=True), ForeignKey('victims.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    measure_number = Column(String(100), nullable=False)
    measure_start_date = Column(Date, nullable=False)
    measure_status = Column(String(50), nullable=False, default='active')
    visit_datetime = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Relationships (opcional, mas útil)
    # victim = relationship("Victim", backref="attendances")
    # user = relationship("User", backref="attendances")
    
    __table_args__ = (
        CheckConstraint(
            "measure_status IN ('active', 'revoked', 'expired', 'suspended')",
            name='chk_measure_status'
        ),
        CheckConstraint(
            "latitude IS NULL OR (latitude >= -90 AND latitude <= 90)",
            name='chk_latitude'
        ),
        CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)",
            name='chk_longitude'
        ),
    )
    
    def __repr__(self):
        return f"<Attendance(id={self.id}, victim_id={self.victim_id}, user_id={self.user_id})>"