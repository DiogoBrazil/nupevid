"""
Utilitários de autenticação e validação
"""
import re
import bcrypt
from email_validator import validate_email, EmailNotValidError

def hash_password(password: str) -> str:
    """
    Gera hash seguro da senha usando bcrypt
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica se a senha corresponde ao hash
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )

def validate_registration(registration: str) -> tuple[bool, str]:
    """
    Valida matrícula do policial
    Deve ter exatamente 9 dígitos começando com 1000
    """
    if not registration:
        return False, "Matrícula é obrigatória"
    
    if len(registration) != 9:
        return False, "Matrícula deve ter exatamente 9 dígitos"
    
    if not registration.isdigit():
        return False, "Matrícula deve conter apenas números"
    
    if not registration.startswith('1000'):
        return False, "Matrícula deve começar com 1000"
    
    return True, ""

def validate_email_format(email: str) -> tuple[bool, str]:
    """
    Valida formato do e-mail
    """
    if not email:
        return False, "E-mail é obrigatório"
    
    try:
        validate_email(email)
        return True, ""
    except EmailNotValidError as e:
        return False, str(e)

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida força da senha (mínimo 6 caracteres)
    """
    if not password:
        return False, "Senha é obrigatória"
    
    if len(password) < 6:
        return False, "Senha deve ter no mínimo 6 caracteres"
    
    return True, ""

def validate_cpf(cpf: str) -> tuple[bool, str]:
    """
    Valida formato básico do CPF (apenas formato, não validação matemática)
    """
    if not cpf:
        return True, ""  # CPF é opcional
    
    # Remove caracteres não numéricos
    cpf_numbers = re.sub(r'\D', '', cpf)
    
    if len(cpf_numbers) != 11:
        return False, "CPF deve ter 11 dígitos"
    
    return True, ""

def format_cpf(cpf: str) -> str:
    """
    Formata CPF para exibição (000.000.000-00)
    """
    if not cpf:
        return ""
    
    cpf_numbers = re.sub(r'\D', '', cpf)
    if len(cpf_numbers) == 11:
        return f"{cpf_numbers[:3]}.{cpf_numbers[3:6]}.{cpf_numbers[6:9]}-{cpf_numbers[9:]}"
    return cpf

def format_phone(phone: str) -> str:
    """
    Formata telefone para exibição
    """
    if not phone:
        return ""
    
    phone_numbers = re.sub(r'\D', '', phone)
    if len(phone_numbers) == 11:
        return f"({phone_numbers[:2]}) {phone_numbers[2:7]}-{phone_numbers[7:]}"
    elif len(phone_numbers) == 10:
        return f"({phone_numbers[:2]}) {phone_numbers[2:6]}-{phone_numbers[6:]}"
    return phone