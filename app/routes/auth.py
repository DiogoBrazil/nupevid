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
        """Página de login"""
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
                            Label("E-mail", _for="email"),
                            Input(
                                type="email",
                                id="email",
                                name="email",
                                placeholder="seu.email@pm.ro.gov.br",
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
                            A("Criar conta", href="/register", cls="btn-secondary"),
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
    def post(email: str, password: str, session):
        """Processa login"""
        success, result = UserService.authenticate(email, password)
        
        if not success:
            return Titled(
                "Login - Patrulha Maria da Penha",
                Main(
                    Card(
                        Div(result, cls="alert alert-error"),
                        H2("Acesso ao Sistema"),
                        Form(
                            Div(
                                Label("E-mail", _for="email"),
                                Input(
                                    type="email",
                                    id="email",
                                    name="email",
                                    value=email,
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
                                A("Criar conta", href="/register", cls="btn-secondary"),
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
        
        return RedirectResponse('/', status_code=303)
    
    @rt('/register', methods='get')
    def get(session):
        """Página de cadastro"""
        # Se já está logado, redireciona para home
        if session.get('user_id'):
            return RedirectResponse('/', status_code=303)
        
        rank_options = [Option(rank, value=rank) for rank in Config.POLICE_RANKS]
        
        return Titled(
            "Cadastro - Patrulha Maria da Penha",
            Main(
                Card(
                    H2("Cadastro de Policial"),
                    P("Preencha todos os campos para criar sua conta", cls="text-muted"),
                    Form(
                        Div(
                            Label("Nome Completo", _for="full_name"),
                            Input(
                                type="text",
                                id="full_name",
                                name="full_name",
                                placeholder="João da Silva",
                                required=True
                            ),
                            cls="form-group"
                        ),
                        Div(
                            Label("Matrícula (9 dígitos, começando com 1000)", _for="registration"),
                            Input(
                                type="text",
                                id="registration",
                                name="registration",
                                placeholder="100012345",
                                required=True,
                                pattern="1000[0-9]{5}",
                                maxlength="9"
                            ),
                            Small("Exemplo: 100012345", cls="help-text"),
                            cls="form-group"
                        ),
                        Div(
                            Label("E-mail", _for="email"),
                            Input(
                                type="email",
                                id="email",
                                name="email",
                                placeholder="seu.email@pm.ro.gov.br",
                                required=True
                            ),
                            cls="form-group"
                        ),
                        Div(
                            Label("Senha (mínimo 6 caracteres)", _for="password"),
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
                            Label("Confirmar Senha", _for="confirm_password"),
                            Input(
                                type="password",
                                id="confirm_password",
                                name="confirm_password",
                                placeholder="••••••••",
                                required=True,
                                minlength="6"
                            ),
                            cls="form-group"
                        ),
                        Div(
                            Label("Posto/Graduação", _for="rank"),
                            Select(
                                *rank_options,
                                id="rank",
                                name="rank",
                                required=True
                            ),
                            cls="form-group"
                        ),
                        Div(
                            Button("Cadastrar", type="submit", cls="btn-primary"),
                            A("Já tenho conta", href="/login", cls="btn-secondary"),
                            cls="button-group"
                        ),
                        method="post",
                        action="/register"
                    ),
                    cls="auth-card"
                ),
                cls="container auth-container"
            )
        )
    
    @rt('/register', methods='post')
    def post(
        full_name: str,
        registration: str,
        email: str,
        password: str,
        confirm_password: str,
        rank: str,
        session
    ):
        """Processa cadastro"""
        # Validação de senha
        if password != confirm_password:
            return Titled(
                "Cadastro - Patrulha Maria da Penha",
                Main(
                    Card(
                        Div("As senhas não coincidem", cls="alert alert-error"),
                        H2("Cadastro de Policial"),
                        # ... (repetir form com dados preenchidos)
                    ),
                    cls="container auth-container"
                )
            )
        
        success, result = UserService.create_user(
            full_name, registration, email, password, rank
        )
        
        if not success:
            rank_options = [Option(r, value=r, selected=(r == rank)) for r in Config.POLICE_RANKS]
            
            return Titled(
                "Cadastro - Patrulha Maria da Penha",
                Main(
                    Card(
                        Div(result, cls="alert alert-error"),
                        H2("Cadastro de Policial"),
                        Form(
                            Div(
                                Label("Nome Completo", _for="full_name"),
                                Input(
                                    type="text",
                                    id="full_name",
                                    name="full_name",
                                    value=full_name,
                                    required=True
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Matrícula", _for="registration"),
                                Input(
                                    type="text",
                                    id="registration",
                                    name="registration",
                                    value=registration,
                                    required=True,
                                    pattern="1000[0-9]{5}",
                                    maxlength="9"
                                ),
                                Small("Exemplo: 100012345", cls="help-text"),
                                cls="form-group"
                            ),
                            Div(
                                Label("E-mail", _for="email"),
                                Input(
                                    type="email",
                                    id="email",
                                    name="email",
                                    value=email,
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
                                Label("Confirmar Senha", _for="confirm_password"),
                                Input(
                                    type="password",
                                    id="confirm_password",
                                    name="confirm_password",
                                    required=True,
                                    minlength="6"
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Posto/Graduação", _for="rank"),
                                Select(*rank_options, id="rank", name="rank", required=True),
                                cls="form-group"
                            ),
                            Div(
                                Button("Cadastrar", type="submit", cls="btn-primary"),
                                A("Já tenho conta", href="/login", cls="btn-secondary"),
                                cls="button-group"
                            ),
                            method="post",
                            action="/register"
                        ),
                        cls="auth-card"
                    ),
                    cls="container auth-container"
                )
            )
        
        # Login automático após cadastro
        success_auth, user_data = UserService.authenticate(email, password)
        if success_auth:
            session['user_id'] = user_data['id']
            session['user_name'] = user_data['full_name']
            session['user_email'] = user_data['email']
            session['user_rank'] = user_data['rank']
        
        return RedirectResponse('/', status_code=303)
    
    @rt('/logout', methods='get')
    def get(session):
        """Logout"""
        session.clear()
        return RedirectResponse('/login', status_code=303)