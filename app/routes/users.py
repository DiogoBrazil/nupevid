"""Rotas de administração e perfil de usuários"""
from fasthtml.common import *
from app.auth.middleware import require_auth, require_admin, get_current_user
from app.services.user_service import UserService
from app.config import Config


def _user_form(action: str, *, full_name: str = "", username: str = "", registration: str = "",
               email: str = "", rank: str = "", role: str = "common", show_role: bool = True,
               show_password: bool = True, is_edit: bool = False, submit_label: str = "Salvar"):
    """Componente reutilizável de formulário de usuário."""
    rank_options = [
        Option(r, value=r, selected=(r == rank)) for r in Config.POLICE_RANKS
    ]

    role_options = [
        Option("Usuário comum", value="common", selected=(role == "common")),
        Option("Administrador", value="admin", selected=(role == "admin")),
    ]

    password_help = "Deixe em branco para manter a senha atual" if is_edit else "Mínimo 6 caracteres"

    fields = [
        Div(
            Label("Nome completo", _for="full_name"),
            Input(
                type="text",
                id="full_name",
                name="full_name",
                value=full_name,
                required=True,
            ),
            cls="form-group",
        ),
        Div(
            Label("Nome de usuário", _for="username"),
            Input(
                type="text",
                id="username",
                name="username",
                value=username,
                required=True,
            ),
            Small("Utilizado no login; deve ser único", cls="help-text"),
            cls="form-group",
        ),
        Div(
            Label("Matrícula (9 dígitos, começando com 1000)", _for="registration"),
            Input(
                type="text",
                id="registration",
                name="registration",
                value=registration,
                placeholder="100012345",
                required=True,
                pattern="1000[0-9]{5}",
                maxlength="9",
            ),
            Small("Exemplo: 100012345", cls="help-text"),
            cls="form-group",
        ),
        Div(
            Label("E-mail", _for="email"),
            Input(
                type="email",
                id="email",
                name="email",
                value=email,
                required=True,
            ),
            cls="form-group",
        ),
        Div(
            Label("Posto/Graduação", _for="rank"),
            Select(
                *rank_options,
                id="rank",
                name="rank",
                required=True,
            ),
            cls="form-group",
        ),
    ]

    if show_role:
        fields.append(
            Div(
                Label("Papel", _for="role"),
                Select(
                    *role_options,
                    id="role",
                    name="role",
                    required=True,
                ),
                Small("Administradores podem gerenciar outros usuários.", cls="help-text"),
                cls="form-group",
            )
        )

    if show_password:
        fields.extend(
            [
                Div(
                    Label("Senha", _for="password"),
                    Input(
                        type="password",
                        id="password",
                        name="password",
                        minlength="6" if not is_edit else None,
                    ),
                    Small(password_help, cls="help-text"),
                    cls="form-group",
                ),
                Div(
                    Label("Confirmar senha", _for="confirm_password"),
                    Input(
                        type="password",
                        id="confirm_password",
                        name="confirm_password",
                        minlength="6" if not is_edit else None,
                    ),
                    cls="form-group",
                ),
            ]
        )

    fields.append(
        Div(
            Button(submit_label, type="submit", cls="btn btn-primary"),
            A("Cancelar", href="/users" if show_role else "/", cls="btn btn-secondary"),
            cls="button-group",
        )
    )

    return Form(
        *fields,
        method="post",
        action=action,
    )


def register_user_routes(app, rt):
    """Registra rotas relacionadas a usuários (admin e perfil)."""

    # ------------------------------------------------------------------
    # Lista de usuários (apenas admin)
    # ------------------------------------------------------------------
    @rt('/users')
    @require_auth
    @require_admin
    def list_users(request, session):
        current = get_current_user(session)
        users = UserService.list_users()

        rows = []
        for u in users:
            rows.append(
                Tr(
                    Td(u['full_name']),
                    Td(u['username']),
                    Td(u['registration']),
                    Td(u['email']),
                    Td(u['rank']),
                    Td("Administrador" if u['role'] == 'admin' else "Comum"),
                    Td(
                        A("Editar", href=f"/users/{u['id']}/edit", cls="btn btn-sm btn-icon btn-icon-edit"),
                        Form(
                            Button("Excluir", type="submit", cls="btn btn-sm btn-danger btn-icon btn-icon-delete"),
                            method="post",
                            action=f"/users/{u['id']}/delete",
                            style="display:inline-block;margin-left:0.5rem;",
                        ),
                        cls="actions",
                    ),
                )
            )

        table = (
            Table(
                Thead(
                    Tr(
                        Th("Nome"),
                        Th("Usuário"),
                        Th("Matrícula"),
                        Th("E-mail"),
                        Th("Posto/Grad."),
                        Th("Papel"),
                        Th("Ações"),
                    )
                ),
                Tbody(*rows) if rows else None,
                cls="data-table",
            )
            if users
            else Div(
                P("Nenhum usuário cadastrado."),
                cls="empty-state",
            )
        )

        header = Header(
            Div(
                H1("Gerenciamento de Usuários"),
                P(f"{current['rank']} {current['name']}", cls="user-info"),
                cls="header-content",
            ),
            Div(
                A("Novo usuário", href="/users/new", cls="btn btn-primary btn-icon btn-icon-add"),
                A("Voltar", href="/", cls="btn btn-secondary"),
                cls="header-actions",
            ),
            cls="main-header",
        )

        return Titled(
            "Usuários - Administração",
            header,
            Main(
                table,
                cls="container",
            ),
        )

    # ------------------------------------------------------------------
    # Criação de usuário (apenas admin)
    # ------------------------------------------------------------------
    @rt('/users/new', methods='get')
    @require_auth
    @require_admin
    def new_user_form(request, session):
        current = get_current_user(session)
        form = _user_form("/users/new", show_role=True, show_password=True, is_edit=False, submit_label="Criar usuário")

        return Titled(
            "Criar Usuário",
            Header(
                Div(
                    H1("Novo usuário"),
                    P(f"{current['rank']} {current['name']}", cls="user-info"),
                    cls="header-content",
                ),
                Div(
                    A("Voltar", href="/users", cls="btn btn-secondary"),
                    cls="header-actions",
                ),
                cls="main-header",
            ),
            Main(
                Card(form, cls="auth-card"),
                cls="container auth-container",
            ),
        )

    @rt('/users/new', methods='post')
    @require_auth
    @require_admin
    def new_user_submit(request, session, form_data: dict):
        data = dict(form_data)

        password = data.get('password') or ""
        confirm_password = data.get('confirm_password') or ""
        if password != confirm_password:
            return Titled(
                "Criar Usuário",
                Main(
                    Div("As senhas não coincidem", cls="alert alert-error"),
                    _user_form(
                        "/users/new",
                        full_name=data.get('full_name', ""),
                        username=data.get('username', ""),
                        registration=data.get('registration', ""),
                        email=data.get('email', ""),
                        rank=data.get('rank', ""),
                        role=data.get('role', "common"),
                        show_role=True,
                        show_password=True,
                        is_edit=False,
                        submit_label="Criar usuário",
                    ),
                    cls="container",
                ),
            )

        success, msg = UserService.create_user(
            data.get('full_name', ""),
            data.get('registration', ""),
            data.get('email', ""),
            password,
            data.get('rank', ""),
            username=data.get('username', ""),
            role=data.get('role', "common"),
        )

        if not success:
            return Titled(
                "Criar Usuário",
                Main(
                    Div(msg, cls="alert alert-error"),
                    _user_form(
                        "/users/new",
                        full_name=data.get('full_name', ""),
                        username=data.get('username', ""),
                        registration=data.get('registration', ""),
                        email=data.get('email', ""),
                        rank=data.get('rank', ""),
                        role=data.get('role', "common"),
                        show_role=True,
                        show_password=True,
                        is_edit=False,
                        submit_label="Criar usuário",
                    ),
                    cls="container",
                ),
            )

        return RedirectResponse('/users', status_code=303)

    # ------------------------------------------------------------------
    # Edição de usuário (apenas admin)
    # ------------------------------------------------------------------
    @rt('/users/{user_id}/edit', methods='get')
    @require_auth
    @require_admin
    def edit_user_form(request, session, user_id: str):
        current = get_current_user(session)
        user = UserService.get_user_by_id(user_id)
        if not user:
            return Titled(
                "Usuário não encontrado",
                Main(
                    Div("Usuário não encontrado", cls="alert alert-error"),
                    A("Voltar", href="/users", cls="btn btn-primary"),
                    cls="container",
                ),
            )

        form = _user_form(
            f"/users/{user_id}/edit",
            full_name=user['full_name'],
            username=user['username'],
            registration=user['registration'],
            email=user['email'],
            rank=user['rank'],
            role=user['role'],
            show_role=True,
            show_password=True,
            is_edit=True,
            submit_label="Salvar alterações",
        )

        return Titled(
            "Editar Usuário",
            Header(
                Div(
                    H1("Editar usuário"),
                    P(f"{current['rank']} {current['name']}", cls="user-info"),
                    cls="header-content",
                ),
                Div(
                    A("Voltar", href="/users", cls="btn btn-secondary"),
                    cls="header-actions",
                ),
                cls="main-header",
            ),
            Main(
                Card(form, cls="auth-card"),
                cls="container auth-container",
            ),
        )

    @rt('/users/{user_id}/edit', methods='post')
    @require_auth
    @require_admin
    def edit_user_submit(request, session, user_id: str, form_data: dict):
        data = dict(form_data)
        password = data.get('password') or None
        confirm_password = data.get('confirm_password') or None

        if password or confirm_password:
            if password != confirm_password:
                user = UserService.get_user_by_id(user_id)
                return Titled(
                    "Editar Usuário",
                    Main(
                        Div("As senhas não coincidem", cls="alert alert-error"),
                        _user_form(
                            f"/users/{user_id}/edit",
                            full_name=data.get('full_name', ""),
                            username=data.get('username', ""),
                            registration=data.get('registration', ""),
                            email=data.get('email', ""),
                            rank=data.get('rank', user['rank'] if user else ""),
                            role=data.get('role', user['role'] if user else "common"),
                            show_role=True,
                            show_password=True,
                            is_edit=True,
                            submit_label="Salvar alterações",
                        ),
                        cls="container",
                    ),
                )

        success, msg = UserService.update_user(
            user_id,
            data.get('full_name', ""),
            data.get('registration', ""),
            data.get('email', ""),
            data.get('rank', ""),
            data.get('username', ""),
            data.get('role', "common"),
            password=password,
        )

        if not success:
            user = UserService.get_user_by_id(user_id)
            return Titled(
                "Editar Usuário",
                Main(
                    Div(msg, cls="alert alert-error"),
                    _user_form(
                        f"/users/{user_id}/edit",
                        full_name=data.get('full_name', user['full_name'] if user else ""),
                        username=data.get('username', user['username'] if user else ""),
                        registration=data.get('registration', user['registration'] if user else ""),
                        email=data.get('email', user['email'] if user else ""),
                        rank=data.get('rank', user['rank'] if user else ""),
                        role=data.get('role', user['role'] if user else "common"),
                        show_role=True,
                        show_password=True,
                        is_edit=True,
                        submit_label="Salvar alterações",
                    ),
                    cls="container",
                ),
            )

        return RedirectResponse('/users', status_code=303)

    # ------------------------------------------------------------------
    # Exclusão de usuário (apenas admin, soft delete)
    # ------------------------------------------------------------------
    @rt('/users/{user_id}/delete', methods='post')
    @require_auth
    @require_admin
    def delete_user(request, session, user_id: str):
        success, _ = UserService.delete_user(user_id, hard_delete=False)
        # Ignora mensagem de erro na UI por simplicidade; poderia ser exibida
        return RedirectResponse('/users', status_code=303)

    # ------------------------------------------------------------------
    # Perfil do usuário logado (pode editar dados próprios, sem ver outros)
    # ------------------------------------------------------------------
    @rt('/profile', methods='get')
    @require_auth
    def profile_form(request, session):
        user = get_current_user(session)
        full = UserService.get_user_by_id(str(user['id']))
        if not full:
            return RedirectResponse('/login', status_code=303)

        form = _user_form(
            "/profile",
            full_name=full['full_name'],
            username=full['username'],
            registration=full['registration'],
            email=full['email'],
            rank=full['rank'],
            role=full['role'],
            show_role=False,  # usuário comum não altera papel
            show_password=True,
            is_edit=True,
            submit_label="Atualizar perfil",
        )

        return Titled(
            "Meu Perfil",
            Header(
                Div(
                    H1("Meu perfil"),
                    P(f"{full['rank']} {full['full_name']}", cls="user-info"),
                    cls="header-content",
                ),
                Div(
                    A("Voltar", href="/", cls="btn btn-secondary"),
                    cls="header-actions",
                ),
                cls="main-header",
            ),
            Main(
                Card(form, cls="auth-card"),
                cls="container auth-container",
            ),
        )

    @rt('/profile', methods='post')
    @require_auth
    def profile_submit(request, session, form_data: dict):
        current = get_current_user(session)
        user_id = str(current['id'])
        data = dict(form_data)

        password = data.get('password') or None
        confirm_password = data.get('confirm_password') or None

        full = UserService.get_user_by_id(user_id)
        if not full:
            return RedirectResponse('/login', status_code=303)

        if password or confirm_password:
            if password != confirm_password:
                return Titled(
                    "Meu Perfil",
                    Main(
                        Div("As senhas não coincidem", cls="alert alert-error"),
                        _user_form(
                            "/profile",
                            full_name=data.get('full_name', full['full_name']),
                            username=data.get('username', full['username']),
                            registration=data.get('registration', full['registration']),
                            email=data.get('email', full['email']),
                            rank=data.get('rank', full['rank']),
                            role=full['role'],
                            show_role=False,
                            show_password=True,
                            is_edit=True,
                            submit_label="Atualizar perfil",
                        ),
                        cls="container",
                    ),
                )

        # Papel sempre mantido, o usuário comum não consegue alterá-lo
        success, msg = UserService.update_user(
            user_id,
            data.get('full_name', full['full_name']),
            data.get('registration', full['registration']),
            data.get('email', full['email']),
            data.get('rank', full['rank']),
            data.get('username', full['username']),
            full['role'],
            password=password,
        )

        if not success:
            return Titled(
                "Meu Perfil",
                Main(
                    Div(msg, cls="alert alert-error"),
                    _user_form(
                        "/profile",
                        full_name=data.get('full_name', full['full_name']),
                        username=data.get('username', full['username']),
                        registration=data.get('registration', full['registration']),
                        email=data.get('email', full['email']),
                        rank=data.get('rank', full['rank']),
                        role=full['role'],
                        show_role=False,
                        show_password=True,
                        is_edit=True,
                        submit_label="Atualizar perfil",
                    ),
                    cls="container",
                ),
            )

        # Atualiza dados básicos na sessão
        session['user_name'] = data.get('full_name', full['full_name'])
        session['user_email'] = data.get('email', full['email'])
        session['user_rank'] = data.get('rank', full['rank'])
        session['user_username'] = data.get('username', full['username'])

        return RedirectResponse('/profile', status_code=303)
