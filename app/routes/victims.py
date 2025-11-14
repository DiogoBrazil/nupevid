"""Rotas de listagem e cadastro/edição de vítimas"""
from datetime import datetime
from fasthtml.common import *
from app.auth.middleware import require_auth, get_current_user
from app.services.victim_service import VictimService
from app.config import Config


def _victim_form(action: str, *, data: dict | None = None, submit_label: str = "Salvar vítima"):
    """Componente reutilizável de formulário de vítima."""
    data = data or {}

    def _get(name: str, default: str = ""):
        return data.get(name, default) or ""

    # Valores para campos especiais
    birth_date_value = ""
    if isinstance(data.get("birth_date"), datetime):
        birth_date_value = data["birth_date"].date().strftime("%Y-%m-%d")
    elif data.get("birth_date"):
        # já vem como date ou string compatível
        try:
            birth_date_value = data["birth_date"].strftime("%Y-%m-%d")  # type: ignore[attr-defined]
        except Exception:
            birth_date_value = str(data["birth_date"])

    address_type_options = [
        Option(t, value=t, selected=(t == _get("address_type")))
        for t in Config.ADDRESS_TYPES
    ]

    state_selected = _get("state", "RO")
    state_options = [
        Option(uf, value=uf, selected=(uf == state_selected))
        for uf in Config.BRAZILIAN_STATES
    ]

    return Form(
        # Seção: Dados da Vítima
        Fieldset(
            Legend("Dados da Vítima"),
            Div(
                Div(
                    Label("Nome completo *", _for="full_name"),
                    Input(
                        type="text",
                        id="full_name",
                        name="full_name",
                        required=True,
                        placeholder="Maria da Silva",
                        value=_get("full_name"),
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Data de nascimento *", _for="birth_date"),
                    Input(
                        type="date",
                        id="birth_date",
                        name="birth_date",
                        required=True,
                        value=birth_date_value,
                    ),
                    cls="form-group",
                ),
                cls="form-row",
            ),
            Div(
                Div(
                    Label("CPF", _for="cpf"),
                    Input(
                        type="text",
                        id="cpf",
                        name="cpf",
                        placeholder="000.000.000-00",
                        maxlength="14",
                        value=_get("cpf"),
                    ),
                    Small("Opcional, mas deve ser único se informado", cls="help-text"),
                    cls="form-group",
                ),
                Div(
                    Label("Telefone principal", _for="phone"),
                    Input(
                        type="tel",
                        id="phone",
                        name="phone",
                        placeholder="(69) 99999-9999",
                        value=_get("phone"),
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Telefone secundário", _for="secondary_phone"),
                    Input(
                        type="tel",
                        id="secondary_phone",
                        name="secondary_phone",
                        placeholder="(69) 99999-9999",
                        value=_get("secondary_phone"),
                    ),
                    cls="form-group",
                ),
                cls="form-row",
            ),
        ),
        # Seção: Endereço
        Fieldset(
            Legend("Endereço"),
            Div(
                Div(
                    Label("CEP", _for="zip_code"),
                    Div(
                        Input(
                            type="text",
                            id="zip_code",
                            name="zip_code",
                            placeholder="76800-000",
                            maxlength="9",
                            value=_get("zip_code"),
                        ),
                        Button(
                            "Buscar CEP",
                            type="button",
                            onclick="buscarCEP()",
                            cls="btn btn-sm",
                        ),
                        cls="input-group",
                    ),
                    Small("Opcional - pode preencher manualmente", cls="help-text"),
                    cls="form-group",
                ),
                cls="form-row",
            ),
            Div(
                Div(
                    Label("Tipo de logradouro", _for="address_type"),
                    Select(
                        *address_type_options,
                        id="address_type",
                        name="address_type",
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Nome do logradouro", _for="address_name"),
                    Input(
                        type="text",
                        id="address_name",
                        name="address_name",
                        placeholder="das Flores",
                        value=_get("address_name"),
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Número", _for="address_number"),
                    Input(
                        type="text",
                        id="address_number",
                        name="address_number",
                        placeholder="123",
                        value=_get("address_number"),
                    ),
                    cls="form-group",
                ),
                cls="form-row",
            ),
            Div(
                Div(
                    Label("Bairro", _for="neighborhood"),
                    Input(
                        type="text",
                        id="neighborhood",
                        name="neighborhood",
                        placeholder="Centro",
                        value=_get("neighborhood"),
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Cidade", _for="city"),
                    Input(
                        type="text",
                        id="city",
                        name="city",
                        placeholder="Porto Velho",
                        value=_get("city"),
                    ),
                    cls="form-group",
                ),
                Div(
                    Label("Estado", _for="state"),
                    Select(
                        *state_options,
                        id="state",
                        name="state",
                    ),
                    cls="form-group",
                ),
                cls="form-row",
            ),
            Div(
                Div(
                    Label("Complemento", _for="address_complement"),
                    Input(
                        type="text",
                        id="address_complement",
                        name="address_complement",
                        placeholder="Apto 201, Bloco B",
                        value=_get("address_complement"),
                    ),
                    cls="form-group",
                ),
                cls="form-row",
            ),
        ),
        # Botões
        Div(
            Button(submit_label, type="submit", cls="btn btn-primary"),
            A("Cancelar", href="/victims", cls="btn btn-secondary"),
            cls="button-group form-actions",
        ),
        method="post",
        action=action,
    )


def register_victim_routes(app, rt):
    """Registra rotas relacionadas a vítimas."""

    # ------------------------------------------------------------------
    # Listagem de vítimas
    # ------------------------------------------------------------------
    @rt('/victims')
    @require_auth
    def list_victims(request, session):
        user = get_current_user(session)
        victims = VictimService.list_victims()

        rows = []
        for v in victims:
            last_visit = (
                v['last_visit'].strftime('%d/%m/%Y %H:%M')
                if v['last_visit']
                else '-'
            )
            rows.append(
                Tr(
                    Td(v['full_name']),
                    Td(v['cpf'] or '-'),
                    Td(v['neighborhood'] or '-'),
                    Td(v['city'] or '-'),
                    Td(last_visit),
                    Td(
                        A(
                            Span("Novo atendimento", cls="btn-text"),
                            href=f"/attendances/new?victim_id={v['id']}",
                            cls="btn btn-sm btn-primary btn-icon btn-icon-service btn-icon-only"
                        ),
                        A(
                            Span("Editar", cls="btn-text"),
                            href=f"/victims/{v['id']}/edit",
                            cls="btn btn-sm btn-secondary btn-icon btn-icon-edit btn-icon-only"
                        ),
                        Form(
                            Button(
                                Span("Excluir", cls="btn-text"),
                                type="submit",
                                cls="btn btn-sm btn-danger btn-icon btn-icon-delete btn-icon-only"
                            ),
                            method="post",
                            action=f"/victims/{v['id']}/delete",
                        ),
                        cls="actions",
                    ),
                )
            )

        table = (
            Table(
                Thead(
                    Tr(
                        Th("Nome Completo"),
                        Th("CPF"),
                        Th("Bairro"),
                        Th("Cidade"),
                        Th("Última Visita"),
                        Th("Ações", cls="text-center"),
                    )
                ),
                Tbody(*rows) if rows else None,
                cls="data-table",
            )
            if victims
            else Div(
                P("Nenhuma vítima cadastrada."),
                A("Cadastrar primeira vítima", href="/victims/new", cls="btn btn-primary"),
                cls="empty-state",
            )
        )

        header = Header(
            Div(
                H1("Vítimas"),
                P(f"{user['rank']} {user['name']}", cls="user-info"),
                cls="header-content",
            ),
            Div(
                A("Nova vítima", href="/victims/new", cls="btn btn-primary btn-icon btn-icon-add"),
                A("Voltar", href="/", cls="btn btn-secondary"),
                cls="header-actions",
            ),
            cls="main-header",
        )

        return Titled(
            "Vítimas cadastradas",
            header,
            Main(
                table,
                cls="container",
            ),
        )

    # ------------------------------------------------------------------
    # Criação de vítima
    # ------------------------------------------------------------------
    @rt('/victims/new', methods='get')
    @require_auth
    def new_victim_form(request, session):
        user = get_current_user(session)
        form = _victim_form("/victims/new")

        return Titled(
            "Nova Vítima",
            Header(
                Div(
                    H1("Cadastrar vítima"),
                    P(f"{user['rank']} {user['name']}", cls="user-info"),
                    cls="header-content",
                ),
                Div(
                    A("Voltar", href="/victims", cls="btn btn-secondary"),
                    cls="header-actions",
                ),
                cls="main-header",
            ),
            Main(
                form,
                cls="container form-container",
            ),
            Script(src="/static/js/cep.js"),
        )

    @rt('/victims/new', methods='post')
    @require_auth
    def new_victim_submit(request, session, form_data: dict):
        data = dict(form_data)

        def parse_date(value: str | None):
            if not value:
                return None
            return datetime.strptime(value, '%Y-%m-%d').date()

        victim_data = {
            'full_name': data.get('full_name'),
            'birth_date': parse_date(data.get('birth_date')),
            'cpf': data.get('cpf'),
            'phone': data.get('phone'),
            'secondary_phone': data.get('secondary_phone'),
            'address_type': data.get('address_type'),
            'address_name': data.get('address_name'),
            'address_number': data.get('address_number'),
            'address_complement': data.get('address_complement'),
            'neighborhood': data.get('neighborhood'),
            'city': data.get('city'),
            'state': data.get('state'),
            'zip_code': data.get('zip_code'),
        }

        success, result = VictimService.create_victim(victim_data)
        if not success:
            # result contém a mensagem de erro
            return Titled(
                "Nova Vítima",
                Main(
                    Div(result, cls="alert alert-error"),
                    _victim_form("/victims/new", data=victim_data),
                    cls="container",
                ),
                Script(src="/static/js/cep.js"),
            )

        return RedirectResponse('/victims', status_code=303)

    # ------------------------------------------------------------------
    # Edição de vítima
    # ------------------------------------------------------------------
    @rt('/victims/{victim_id}/edit', methods='get')
    @require_auth
    def edit_victim_form(request, session, victim_id: str):
        user = get_current_user(session)
        victim = VictimService.get_victim_by_id(victim_id)
        if not victim:
            return Titled(
                "Vítima não encontrada",
                Main(
                    Div("Vítima não encontrada", cls="alert alert-error"),
                    A("Voltar", href="/victims", cls="btn btn-primary"),
                    cls="container",
                ),
            )

        form = _victim_form(f"/victims/{victim_id}/edit", data=victim, submit_label="Salvar alterações")

        return Titled(
            "Editar Vítima",
            Header(
                Div(
                    H1("Editar vítima"),
                    P(f"{user['rank']} {user['name']}", cls="user-info"),
                    cls="header-content",
                ),
                Div(
                    A("Voltar", href="/victims", cls="btn btn-secondary"),
                    cls="header-actions",
                ),
                cls="main-header",
            ),
            Main(
                form,
                cls="container form-container",
            ),
            Script(src="/static/js/cep.js"),
        )

    @rt('/victims/{victim_id}/edit', methods='post')
    @require_auth
    def edit_victim_submit(request, session, victim_id: str, form_data: dict):
        data = dict(form_data)

        def parse_date(value: str | None):
            if not value:
                return None
            return datetime.strptime(value, '%Y-%m-%d').date()

        victim_data = {
            'full_name': data.get('full_name'),
            'birth_date': parse_date(data.get('birth_date')),
            'cpf': data.get('cpf'),
            'phone': data.get('phone'),
            'secondary_phone': data.get('secondary_phone'),
            'address_type': data.get('address_type'),
            'address_name': data.get('address_name'),
            'address_number': data.get('address_number'),
            'address_complement': data.get('address_complement'),
            'neighborhood': data.get('neighborhood'),
            'city': data.get('city'),
            'state': data.get('state'),
            'zip_code': data.get('zip_code'),
        }

        success, result = VictimService.update_victim(victim_id, victim_data)
        if not success:
            return Titled(
                "Editar Vítima",
                Main(
                    Div(result, cls="alert alert-error"),
                    _victim_form(f"/victims/{victim_id}/edit", data=victim_data, submit_label="Salvar alterações"),
                    cls="container",
                ),
                Script(src="/static/js/cep.js"),
            )

        return RedirectResponse('/victims', status_code=303)

    # ------------------------------------------------------------------
    # Exclusão de vítima
    # ------------------------------------------------------------------
    @rt('/victims/{victim_id}/delete', methods='post')
    @require_auth
    def delete_victim(request, session, victim_id: str):
        success, _ = VictimService.delete_victim(victim_id)
        # Poderíamos exibir mensagem de erro, mas para simplicidade sempre voltamos à lista
        return RedirectResponse('/victims', status_code=303)
