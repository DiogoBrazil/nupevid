"""
Serviço de gerenciamento de vítimas usando SQLAlchemy
"""
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.db import db
from app.models.victim import Victim
from app.models.attendance import Attendance
from app.auth.utils import validate_cpf
from uuid import UUID

class VictimService:
    """Serviço para operações com vítimas"""
    
    @staticmethod
    def create_victim(victim_data):
        """Cria uma nova vítima.

        - CPF é opcional, mas se informado deve ser válido e único.
        """
        # Validação de CPF se fornecido
        if victim_data.get('cpf'):
            valid_cpf, msg_cpf = validate_cpf(victim_data['cpf'])
            if not valid_cpf:
                return False, msg_cpf

        try:
            with db.get_session() as session:
                # Garante unicidade por CPF, se informado
                cpf = victim_data.get('cpf')
                if cpf:
                    existing = session.execute(
                        select(Victim).where(Victim.cpf == cpf)
                    ).scalar_one_or_none()
                    if existing:
                        return False, "Já existe uma vítima cadastrada com este CPF."

                victim = Victim(
                    full_name=victim_data['full_name'],
                    birth_date=victim_data['birth_date'],
                    cpf=victim_data.get('cpf'),
                    phone=victim_data.get('phone'),
                    secondary_phone=victim_data.get('secondary_phone'),
                    address_type=victim_data.get('address_type'),
                    address_name=victim_data.get('address_name'),
                    address_number=victim_data.get('address_number'),
                    address_complement=victim_data.get('address_complement'),
                    neighborhood=victim_data.get('neighborhood'),
                    city=victim_data.get('city'),
                    state=victim_data.get('state'),
                    zip_code=victim_data.get('zip_code'),
                )

                session.add(victim)
                session.flush()

                return True, str(victim.id)
        except IntegrityError:
            # Reflete violação da constraint única no CPF
            return False, "Já existe uma vítima cadastrada com este CPF."
        except Exception as e:
            return False, f"Erro ao criar vítima: {str(e)}"
    
    @staticmethod
    def get_victim_by_id(victim_id):
        """
        Busca vítima por ID
        """
        try:
            with db.get_session() as session:
                try:
                    vid = UUID(victim_id) if isinstance(victim_id, str) else victim_id
                except Exception:
                    vid = victim_id

                victim = session.execute(
                    select(Victim).where(Victim.id == vid)
                ).scalar_one_or_none()
                
                if not victim:
                    return None
                
                return {
                    'id': victim.id,
                    'full_name': victim.full_name,
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
                    'zip_code': victim.zip_code
                }
        except Exception as e:
            return None
    
    @staticmethod
    def list_victims():
        """Lista todas as vítimas com data da última visita."""
        try:
            with db.get_session() as session:
                # Query com left join para pegar a última visita
                stmt = select(
                    Victim.id,
                    Victim.full_name,
                    Victim.cpf,
                    Victim.neighborhood,
                    Victim.city,
                    func.max(Attendance.visit_datetime).label('last_visit'),
                ).outerjoin(
                    Attendance, Victim.id == Attendance.victim_id
                ).group_by(
                    Victim.id,
                    Victim.full_name,
                    Victim.cpf,
                    Victim.neighborhood,
                    Victim.city,
                ).order_by(
                    func.max(Attendance.visit_datetime).desc().nulls_last()
                )

                result = session.execute(stmt).all()

                return [
                    {
                        'id': row.id,
                        'full_name': row.full_name,
                        'cpf': row.cpf,
                        'neighborhood': row.neighborhood,
                        'city': row.city,
                        'last_visit': row.last_visit,
                    }
                    for row in result
                ]
        except Exception:
            return []

    @staticmethod
    def update_victim(victim_id: str, victim_data: dict):
        """Atualiza dados de uma vítima existente."""
        # Validação de CPF se fornecido
        if victim_data.get('cpf'):
            valid_cpf, msg_cpf = validate_cpf(victim_data['cpf'])
            if not valid_cpf:
                return False, msg_cpf

        try:
            with db.get_session() as session:
                try:
                    vid = UUID(victim_id) if isinstance(victim_id, str) else victim_id
                except Exception:
                    vid = victim_id

                victim = session.execute(
                    select(Victim).where(Victim.id == vid)
                ).scalar_one_or_none()

                if not victim:
                    return False, "Vítima não encontrada"

                cpf = victim_data.get('cpf')
                if cpf:
                    existing = session.execute(
                        select(Victim).where(
                            (Victim.cpf == cpf) & (Victim.id != vid)
                        )
                    ).scalar_one_or_none()
                    if existing:
                        return False, "Já existe uma vítima cadastrada com este CPF."

                victim.full_name = victim_data['full_name']
                victim.birth_date = victim_data['birth_date']
                victim.cpf = victim_data.get('cpf')
                victim.phone = victim_data.get('phone')
                victim.secondary_phone = victim_data.get('secondary_phone')
                victim.address_type = victim_data.get('address_type')
                victim.address_name = victim_data.get('address_name')
                victim.address_number = victim_data.get('address_number')
                victim.address_complement = victim_data.get('address_complement')
                victim.neighborhood = victim_data.get('neighborhood')
                victim.city = victim_data.get('city')
                victim.state = victim_data.get('state')
                victim.zip_code = victim_data.get('zip_code')

                session.flush()
                return True, str(victim.id)
        except IntegrityError:
            return False, "Já existe uma vítima cadastrada com este CPF."
        except Exception as e:
            return False, f"Erro ao atualizar vítima: {str(e)}"

    @staticmethod
    def delete_victim(victim_id: str):
        """Remove uma vítima e, devido ao CASCADE, seus atendimentos associados."""
        try:
            with db.get_session() as session:
                try:
                    vid = UUID(victim_id) if isinstance(victim_id, str) else victim_id
                except Exception:
                    vid = victim_id

                victim = session.execute(
                    select(Victim).where(Victim.id == vid)
                ).scalar_one_or_none()

                if not victim:
                    return False, "Vítima não encontrada"

                session.delete(victim)
                session.flush()
                return True, "Vítima removida com sucesso"
        except Exception as e:
            return False, f"Erro ao remover vítima: {str(e)}"
