"""
Middleware de autenticação
"""
from functools import wraps
from fasthtml.common import *


def require_auth(func):
    """Decorator para proteger rotas que requerem autenticação"""
    @wraps(func)
    def wrapper(request, session, *args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return RedirectResponse('/login', status_code=303)
        return func(request, session, *args, **kwargs)

    return wrapper


def require_admin(func):
    """Decorator para rotas restritas a administradores"""
    @wraps(func)
    def wrapper(request, session, *args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return RedirectResponse('/login', status_code=303)

        if session.get('user_role') != 'admin':
            # Usuário autenticado, porém sem permissão
            return Titled(
                "Acesso negado",
                Main(
                    Div("Você não tem permissão para acessar esta página.", cls="alert alert-error"),
                    A("Voltar", href="/", cls="btn btn-primary"),
                    cls="container"
                )
            )

        return func(request, session, *args, **kwargs)

    return wrapper


def get_current_user(session):
    """Retorna dados do usuário logado a partir da sessão"""
    return {
        'id': session.get('user_id'),
        'name': session.get('user_name'),
        'rank': session.get('user_rank'),
        'email': session.get('user_email'),
        'role': session.get('user_role'),
        'username': session.get('user_username'),
    }
