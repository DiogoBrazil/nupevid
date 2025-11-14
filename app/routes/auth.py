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
        """Página de login (somente acesso, sem auto-cadastro)"""
        # Se já está logado, redireciona para home
        if session.get('user_id'):
            return RedirectResponse('/', status_code=303)

        return Titled(
            "Login - Patrulha Maria da Penha",
            Main(
                Card(
                    H2("Acesso ao Sistema"),
                    P("Entre com suas credenciais", cls="text-muted"),
                    Form(
                        Div(
                            Label("Login", _for="login"),
                            Input(
                                type="text",
                                id="login",
                                name="login",
                                placeholder="usuário ou e-mail",
                                required=True
                            ),
                            cls="form-group"
                        ),
                        Div(
                            Label("Senha", _for="password"),
                            Input(
                                type="password",
                                id="password",
                                name="password",
                                placeholder="••••••••",
                                required=True,
                                minlength="6"
                            ),
                            cls="form-group"
                        ),
                        Div(
                            Button("Entrar", type="submit", cls="btn-primary"),
                            cls="button-group"
                        ),
                        method="post",
                        action="/login"
                    ),
                    cls="auth-card"
                ),
                cls="container auth-container"
            )
        )
    
    @rt('/login', methods='post')
    def post(login: str, password: str, session):
        """Processa login"""
        success, result = UserService.authenticate(login, password)

        if not success:
            return Titled(
                "Login - Patrulha Maria da Penha",
                Main(
                    Card(
                        Div(result, cls="alert alert-error"),
                        H2("Acesso ao Sistema"),
                        Form(
                            Div(
                                Label("Login", _for="login"),
                                Input(
                                    type="text",
                                    id="login",
                                    name="login",
                                    value=login,
                                    required=True
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Senha", _for="password"),
                                Input(
                                    type="password",
                                    id="password",
                                    name="password",
                                    required=True,
                                    minlength="6"
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Button("Entrar", type="submit", cls="btn-primary"),
                                cls="button-group"
                            ),
                            method="post",
                            action="/login"
                        ),
                        cls="auth-card"
                    ),
                    cls="container auth-container"
                )
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