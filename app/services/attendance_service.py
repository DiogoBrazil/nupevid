"""
Serviço de gerenciamento de atendimentos usando SQLAlchemy
"""
from sqlalchemy import select
from app.db import db
from app.models.attendance import Attendance
from app.models.victim import Victim
from app.models.user import User
from uuid import UUID

class AttendanceService:
    """Serviço para operações com atendimentos"""
    
    @staticmethod
    def create_attendance(attendance_data):
        """
        Cria um novo atendimento
        """
        try:
            with db.get_session() as session:
                # convert string ids to UUID objects when needed
                try:
                    vid = UUID(attendance_data['victim_id']) if isinstance(attendance_data['victim_id'], str) else attendance_data['victim_id']
                except Exception:
                    vid = attendance_data['victim_id']

                try:
                    uid = UUID(attendance_data['user_id']) if isinstance(attendance_data['user_id'], str) else attendance_data['user_id']
                except Exception:
                    uid = attendance_data['user_id']

                attendance = Attendance(
                    victim_id=vid,
                    user_id=uid,
                    measure_number=attendance_data['measure_number'],
                    measure_start_date=attendance_data['measure_start_date'],
                    measure_status=attendance_data['measure_status'],
                    visit_datetime=attendance_data['visit_datetime'],
                    notes=attendance_data.get('notes'),
                    latitude=attendance_data.get('latitude'),
                    longitude=attendance_data.get('longitude')
                )
                
                session.add(attendance)
                session.flush()
                
                return True, str(attendance.id)
        except Exception as e:
            return False, f"Erro ao criar atendimento: {str(e)}"
    
    @staticmethod
    def get_attendance_by_id(attendance_id):
        """
        Busca atendimento por ID com dados completos
        """
        try:
            with db.get_session() as session:
                try:
                    aid = UUID(attendance_id) if isinstance(attendance_id, str) else attendance_id
                except Exception:
                    aid = attendance_id

                stmt = select(
                    Attendance,
                    Victim,
                    User
                ).join(
                    Victim, Attendance.victim_id == Victim.id
                ).join(
                    User, Attendance.user_id == User.id
                ).where(
                    Attendance.id == aid
                )
                
                result = session.execute(stmt).one_or_none()
                
                if not result:
                    return None
                
                attendance, victim, user = result
                
                return {
                    'id': attendance.id,
                    'victim_id': attendance.victim_id,
                    'user_id': attendance.user_id,
                    'measure_number': attendance.measure_number,
                    'measure_start_date': attendance.measure_start_date,
                    'measure_status': attendance.measure_status,
                    'visit_datetime': attendance.visit_datetime,
                    'notes': attendance.notes,
                    'latitude': attendance.latitude,
                    'longitude': attendance.longitude,
                    'created_at': attendance.created_at,
                    # Dados da vítima
                    'victim_name': victim.full_name,
                    'birth_date': victim.birth_date,
                    'cpf': victim.cpf,
                    'phone': victim.phone,
                    'secondary_phone': victim.secondary_phone,
                    'address_type': victim.address_type,
                    'address_name': victim.address_name,
                    'address_number': victim.address_number,
                    'address_complement': victim.address_complement,
                    'neighborhood': victim.neighborhood,
                    'city': victim.city,
                    'state': victim.state,
                    'zip_code': victim.zip_code,
                    # Dados do policial
                    'officer_name': user.full_name,
                    'officer_rank': user.rank
                }
        except Exception as e:
            return None
    
    @staticmethod
    def list_attendances():
        """
        Lista todos os atendimentos
        """
        try:
            with db.get_session() as session:
                stmt = select(
                    Attendance.id,
                    Attendance.visit_datetime,
                    Attendance.measure_number,
                    Victim.full_name.label('victim_name'),
                    Victim.neighborhood,
                    User.full_name.label('officer_name'),
                    User.rank.label('officer_rank')
                ).join(
                    Victim, Attendance.victim_id == Victim.id
                ).join(
                    User, Attendance.user_id == User.id
                ).order_by(
                    Attendance.visit_datetime.desc()
                )
                
                result = session.execute(stmt).all()
                
                return [
                    {
                        'id': row.id,
                        'visit_datetime': row.visit_datetime,
                        'measure_number': row.measure_number,
                        'victim_name': row.victim_name,
                        'neighborhood': row.neighborhood,
                        'officer_name': row.officer_name,
                        'officer_rank': row.officer_rank
                    }
                    for row in result
                ]
        except Exception as e:
            return []
    
    @staticmethod
    def get_attendances_by_victim(victim_id):
        """
        Lista atendimentos de uma vítima específica
        """
        try:
            with db.get_session() as session:
                try:
                    vid = UUID(victim_id) if isinstance(victim_id, str) else victim_id
                except Exception:
                    vid = victim_id

                stmt = select(
                    Attendance,
                    User.full_name.label('officer_name'),
                    User.rank.label('officer_rank')
                ).join(
                    User, Attendance.user_id == User.id
                ).where(
                    Attendance.victim_id == vid
                ).order_by(
                    Attendance.visit_datetime.desc()
                )
                
                result = session.execute(stmt).all()
                
                attendances = []
                for row in result:
                    att = row.Attendance
                    attendances.append({
                        'id': att.id,
                        'measure_number': att.measure_number,
                        'measure_start_date': att.measure_start_date,
                        'measure_status': att.measure_status,
                        'visit_datetime': att.visit_datetime,
                        'notes': att.notes,
                        'latitude': att.latitude,
                        'longitude': att.longitude,
                        'officer_name': row.officer_name,
                        'officer_rank': row.officer_rank
                    })
                
                return attendances
        except Exception as e:
            return []