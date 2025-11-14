"""
Configurações do projeto NUPEVID
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)


class Config:
    """Configurações da aplicação"""
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/nupevid')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
    SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME', 'nupevid_session')
    SESSION_MAX_AGE = int(os.getenv('SESSION_MAX_AGE', '3600'))
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8000'))
    
    # Postos e Graduações da PM
    POLICE_RANKS = [
        'CEL PM',
        'TC PM',
        'MAJ PM',
        'CAP PM',
        '1º TEN PM',
        '2º TEN PM',
        'ASP OF PM',
        'ST PM',
        '1º SGT PM',
        '2º SGT PM',
        '3º SGT PM',
        'CB PM',
        'SD PM'
    ]
    
    # Tipos de logradouro
    ADDRESS_TYPES = [
        'Rua',
        'Avenida',
        'Travessa',
        'Alameda',
        'Rodovia',
        'Estrada',
        'Praça',
        'Quadra',
        'Lote',
        'Sítio',
        'Fazenda',
        'Linha',
        'Gleba',
        'Vicinal',
        'Ramal'
    ]
    
    # Estados brasileiros
    BRAZILIAN_STATES = [
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    ]
    
    # Status das medidas protetivas
    MEASURE_STATUS = [
        ('active', 'Ativa'),
        ('revoked', 'Revogada'),
        ('expired', 'Expirada'),
        ('suspended', 'Suspensa')
    ]
