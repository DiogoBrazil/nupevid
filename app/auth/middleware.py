"""
Middleware de autenticação
"""
from functools import wraps
from fasthtml.common import *

def require_auth(func):
    """
    Decorator para proteger rotas que requerem autenticação
    """
    @wraps(func)
    def wrapper(request, session, *args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return RedirectResponse('/login', status_code=303)
        return func(request, session, *args, **kwargs)
    return wrapper

def get_current_user(session):
    """
    Retorna dados do usuário logado
    """
    return {
        'id': session.get('user_id'),
        'name': session.get('user_name'),
        'rank': session.get('user_rank'),
        'email': session.get('user_email')
    }