"""
Rotas de autenticação
"""
from fasthtml.common import *
from app.auth.middleware import require_auth, get_current_user
from app.services.user_service import UserService
from app.config import Config

def register_auth_routes(app, rt):
    """Registra rotas de autenticação"""
    
    @rt('/login', methods='get')
    def get(session):
        """Página de login (somente acesso, sem auto-cadastro)."""
        # Se já está logado, redireciona para home
        if session.get('user_id'):
            return RedirectResponse('/', status_code=303)

        return (
            Title("NUPEVID/7ºBPM"),
            Main(
                Div(
                    Div(
                        Form(
                            Div("NUPEVID/7ºBPM", cls="login-logo"),
                            Div("Sistema de Atendimento – Patrulha Maria da Penha", cls="login-subtitle"),
                            Input(
                                type="text",
                                id="login",
                                name="login",
                                placeholder="E-mail",
                                required=True,
                                cls="login-input-pill",
                            ),
                            Input(
                                type="password",
                                id="password",
                                name="password",
                                placeholder="Senha",
                                required=True,
                                minlength="6",
                                cls="login-input-pill",
                            ),
                            Button("Entrar", type="submit", cls="btn-primary login-pill-submit"),
                            method="post",
                            action="/login",
                            cls="login-hero-form",
                        ),
                        cls="login-hero",
                    ),
                    cls="login-hero-container",
                ),
            ),
        )

    @rt('/login', methods='post')
    def post(login: str, password: str, session):
        """Processa login"""
        success, result = UserService.authenticate(login, password)

        if not success:
            return (
                Title("NUPEVID/7ºBPM"),
                Main(
                    Div(
                        Div(
                            Form(
                                Div("NUPEVID/7ºBPM", cls="login-logo"),
                                Div("Sistema de Atendimento – Patrulha Maria da Penha", cls="login-subtitle"),
                                Div(result, cls="alert alert-error"),
                                Input(
                                    type="text",
                                    id="login",
                                    name="login",
                                    value=login,
                                    placeholder="E-mail",
                                    required=True,
                                    cls="login-input-pill",
                                ),
                                Input(
                                    type="password",
                                    id="password",
                                    name="password",
                                    placeholder="Senha",
                                    required=True,
                                    minlength="6",
                                    cls="login-input-pill",
                                ),
                                Button("Entrar", type="submit", cls="btn-primary login-pill-submit"),
                                method="post",
                                action="/login",
                                cls="login-hero-form",
                            ),
                            cls="login-hero",
                        ),
                        cls="login-hero-container",
                    ),
                ),
            )

        # Salvar dados na sessão
        session['user_id'] = result['id']
        session['user_name'] = result['full_name']
        session['user_email'] = result['email']
        session['user_rank'] = result['rank']
        session['user_role'] = result['role']
        session['user_username'] = result['username']

        return RedirectResponse('/', status_code=303)

    @rt('/logout', methods='get')
    def get(session):
        """Logout"""
        session.clear()
        return RedirectResponse('/login', status_code=303)