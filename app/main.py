"""
Aplicação principal - Patrulha Maria da Penha
Sistema de registro de atendimentos e medidas protetivas
"""
import sys
from pathlib import Path

# Garantir que o diretório raiz esteja no PYTHONPATH ao executar app/main.py diretamente
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from fasthtml.common import *
from app.config import Config
from app.routes.auth import register_auth_routes
from app.routes.users import register_user_routes
from app.routes.victims import register_victim_routes
from app.routes.attendances import register_attendance_routes

# Criação da aplicação FastHTML
app = FastHTML(
    debug=Config.DEBUG,
    secret_key=Config.SECRET_KEY,
    session_cookie=Config.SESSION_COOKIE_NAME,
    max_age=Config.SESSION_MAX_AGE,
    hdrs=(
        # Link para CSS customizado
        Link(rel='stylesheet', href='/static/css/style.css', type='text/css'),
        # Meta tags
        Meta(charset='utf-8'),
        Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
        Meta(name='description', content='Sistema de Atendimento - Patrulha Maria da Penha'),
    )
)

# Atalho para rotas
rt = app.route

# Registra rotas de autenticação
register_auth_routes(app, rt)

# Rotas de administração / perfil de usuários
register_user_routes(app, rt)

# Rotas de vítimas
register_victim_routes(app, rt)

# Registra rotas de atendimentos
register_attendance_routes(app, rt)

# Rota para arquivos estáticos
@rt('/{filepath:path}')
def static_files(filepath: str):
    """Serve arquivos estáticos"""
    if filepath.startswith('static/'):
        return FileResponse(filepath)
    return Response("Not Found", status_code=404)

# Rota 404
@app.exception_handler(404)
def not_found(request, exc):
    """Página 404"""
    return Titled(
        "Página não encontrada",
        Container(
            Card(
                H2("404 - Página não encontrada"),
                P("A página que você está procurando não existe."),
                A("Voltar para o início", href="/", cls="btn btn-primary")
            )
        )
    )

# Rota de erro 500
@app.exception_handler(500)
def server_error(request, exc):
    """Página 500"""
    return Titled(
        "Erro no servidor",
        Container(
            Card(
                H2("500 - Erro no servidor"),
                P("Ocorreu um erro inesperado. Por favor, tente novamente."),
                A("Voltar para o início", href="/", cls="btn btn-primary")
            )
        )
    )

if __name__ == '__main__':
    # Inicia o servidor (appname explicito garante import correto `app.main:app` ao usar serve)
    serve(
        appname='app.main',
        app='app',
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    )