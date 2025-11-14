"""
Rotas de atendimentos
"""
from fasthtml.common import *
from datetime import datetime
from app.auth.middleware import require_auth, get_current_user
from app.services.victim_service import VictimService
from app.services.attendance_service import AttendanceService
from app.config import Config

def register_attendance_routes(app, rt):
    """Registra rotas de atendimentos"""
    
    @rt('/')
    @require_auth
    def get(request, session):
        """Página inicial - lista de atendimentos"""
        user = get_current_user(session)
        attendances = AttendanceService.list_attendances()
        
        # Header com informações do usuário
        header = Header(
            Div(
                H1("Patrulha Maria da Penha"),
                P(f"{user['rank']} {user['name']}", cls="user-info"),
                cls="header-content"
            ),
            Div(
                A("Vítimas", href="/victims", cls="btn btn-primary"),
                A("Meu perfil", href="/profile", cls="btn btn-secondary"),
                A("Sair", href="/logout", cls="btn btn-secondary"),
                cls="header-actions"
            ),
            cls="main-header"
        )
        
        # Tabela de atendimentos
        if attendances:
            rows = []
            for att in attendances:
                visit_date = att['visit_datetime'].strftime('%d/%m/%Y %H:%M') if att['visit_datetime'] else '-'
                rows.append(
                    Tr(
                        Td(visit_date),
                        Td(att['victim_name']),
                        Td(att['neighborhood'] or '-'),
                        Td(att['measure_number']),
                        Td(f"{att['officer_rank']} {att['officer_name']}"),
                        Td(
                            A("Ver detalhes", href=f"/attendances/{att['id']}", cls="btn btn-sm btn-icon btn-icon-view"),
                            cls="actions"
                        )
                    )
                )
            
            table = Table(
                Thead(
                    Tr(
                        Th("Data/Hora"),
                        Th("Vítima"),
                        Th("Bairro"),
                        Th("Medida Protetiva"),
                        Th("Policial"),
                        Th("Ações")
                    )
                ),
                Tbody(*rows),
                cls="data-table"
            )
        else:
            table = Div(
                P("Nenhum atendimento registrado ainda."),
                P("Cadastre uma vítima e, em seguida, registre o atendimento."),
                A("Cadastrar primeira vítima", href="/victims/new", cls="btn btn-primary"),
                cls="empty-state"
            )
        
        return Titled(
            "Patrulha Maria da Penha - Sistema de Atendimentos",
            header,
            Main(
                H2("Atendimentos Registrados"),
                table,
                cls="container"
            )
        )
    
    @rt('/attendances/new', methods='get')
    @require_auth
    def get(request, session, victim_id: str | None = None):
        """Formulário de novo atendimento para uma vítima já cadastrada."""
        user = get_current_user(session)

        # Se nenhuma vítima foi informada, orienta o usuário a ir para a lista de vítimas
        if not victim_id:
            return Titled(
                "Novo Atendimento - Selecione a vítima",
                Header(
                    Div(
                        H1("Novo atendimento"),
                        P(f"{user['rank']} {user['name']}", cls="user-info"),
                        cls="header-content",
                    ),
                    Div(
                        A("Ir para lista de vítimas", href="/victims", cls="btn btn-primary"),
                        A("Cadastrar nova vítima", href="/victims/new", cls="btn btn-secondary"),
                        A("Voltar", href="/", cls="btn btn-secondary"),
                        cls="header-actions",
                    ),
                    cls="main-header",
                ),
                Main(
                    Div(
                        P("Para registrar um atendimento, primeiro selecione a vítima na lista."),
                        cls="empty-state",
                    ),
                    cls="container",
                ),
            )

        victim = VictimService.get_victim_by_id(victim_id)
        if not victim:
            return Titled(
                "Vítima não encontrada",
                Main(
                    Div("Vítima não encontrada", cls="alert alert-error"),
                    A("Voltar para lista de vítimas", href="/victims", cls="btn btn-primary"),
                    cls="container",
                ),
            )

        status_options = [
            Option(label, value=value)
            for value, label in Config.MEASURE_STATUS
        ]

        # Dados formatados da vítima (somente leitura)
        birth_date_str = victim['birth_date'].strftime('%d/%m/%Y') if victim['birth_date'] else '-'

        address_parts = []
        if victim['address_type'] and victim['address_name']:
            address_parts.append(f"{victim['address_type']} {victim['address_name']}")
        if victim['address_number']:
            address_parts.append(f"nº {victim['address_number']}")
        if victim['address_complement']:
            address_parts.append(victim['address_complement'])
        full_address = ", ".join(address_parts) if address_parts else "Não informado"

        location_parts = []
        if victim['neighborhood']:
            location_parts.append(victim['neighborhood'])
        if victim['city']:
            location_parts.append(victim['city'])
        if victim['state']:
            location_parts.append(victim['state'])
        full_location = " - ".join(location_parts) if location_parts else "Não informado"

        return Titled(
            "Novo Atendimento - Patrulha Maria da Penha",
            Header(
                Div(
                    H1("Novo atendimento"),
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
                Form(
                    # Vítima selecionada (somente leitura)
                    Input(type="hidden", id="victim_id", name="victim_id", value=str(victim['id'])),
                    Fieldset(
                        Legend("Vítima selecionada"),
                        Dl(
                            Dt("Nome:"), Dd(victim['full_name']),
                            Dt("Data de nascimento:"), Dd(birth_date_str),
                            Dt("CPF:"), Dd(victim['cpf'] or "Não informado"),
                            Dt("Telefone:"), Dd(victim['phone'] or "Não informado"),
                            Dt("Telefone secundário:"), Dd(victim['secondary_phone'] or "Não informado"),
                            Dt("Endereço:"), Dd(full_address),
                            Dt("Localidade:"), Dd(full_location),
                            Dt("CEP:"), Dd(victim['zip_code'] or "Não informado"),
                            cls="details-list",
                        ),
                    ),

                    # Seção: Medida Protetiva
                    Fieldset(
                        Legend("Medida Protetiva"),
                        Div(
                            Div(
                                Label("Número da Medida *", _for="measure_number"),
                                Input(
                                    type="text",
                                    id="measure_number",
                                    name="measure_number",
                                    required=True,
                                    placeholder="0000000-00.0000.0.00.0000",
                                ),
                                cls="form-group",
                            ),
                            Div(
                                Label("Data de Início *", _for="measure_start_date"),
                                Input(
                                    type="date",
                                    id="measure_start_date",
                                    name="measure_start_date",
                                    required=True,
                                ),
                                cls="form-group",
                            ),
                            Div(
                                Label("Situação *", _for="measure_status"),
                                Select(
                                    *status_options,
                                    id="measure_status",
                                    name="measure_status",
                                    required=True,
                                ),
                                cls="form-group",
                            ),
                            cls="form-row",
                        ),
                    ),

                    # Seção: Atendimento
                    Fieldset(
                        Legend("Dados do Atendimento"),
                        Div(
                            Div(
                                Label("Data/Hora da Visita *", _for="visit_datetime"),
                                Input(
                                    type="datetime-local",
                                    id="visit_datetime",
                                    name="visit_datetime",
                                    required=True,
                                    value=datetime.now().strftime('%Y-%m-%dT%H:%M'),
                                ),
                                cls="form-group",
                            ),
                            cls="form-row",
                        ),
                        Div(
                            Div(
                                Label("Observações", _for="notes"),
                                Textarea(
                                    id="notes",
                                    name="notes",
                                    rows="4",
                                    placeholder="Descreva detalhes da visita, situação encontrada, etc.",
                                ),
                                cls="form-group",
                            ),
                            cls="form-row",
                        ),
                    ),

                    # Seção: Geolocalização
                    Fieldset(
                        Legend("Geolocalização (Opcional)"),
                        Div(
                            P("A coleta de localização é opcional, mas ajuda em análises futuras."),
                            cls="info-message",
                        ),
                        Div(
                            Div(
                                Label("Latitude", _for="latitude"),
                                Input(
                                    type="text",
                                    id="latitude",
                                    name="latitude",
                                    placeholder="-8.7612",
                                    readonly=True,
                                ),
                                cls="form-group",
                            ),
                            Div(
                                Label("Longitude", _for="longitude"),
                                Input(
                                    type="text",
                                    id="longitude",
                                    name="longitude",
                                    placeholder="-63.9004",
                                    readonly=True,
                                ),
                                cls="form-group",
                            ),
                            cls="form-row",
                        ),
                        Div(
                            Button(
                                "📍 Capturar Localização",
                                type="button",
                                onclick="captureLocation()",
                                cls="btn btn-secondary",
                                id="capture-btn",
                            ),
                            Button(
                                "🗺️ Conferir no Mapa",
                                type="button",
                                onclick="checkOnMap()",
                                cls="btn btn-secondary",
                                id="map-btn",
                                style="display:none;",
                            ),
                            cls="button-group",
                        ),
                        Div(id="location-status", cls="status-message"),
                    ),

                    # Botões de ação
                    Div(
                        Button("Salvar Atendimento", type="submit", cls="btn btn-primary"),
                        A("Cancelar", href="/victims", cls="btn btn-secondary"),
                        cls="button-group form-actions",
                    ),

                    method="post",
                    action=f"/attendances/new?victim_id={victim_id}",
                ),
                cls="container form-container",
            ),
            Script(src="/static/js/geolocation.js"),
        )
    
    @rt('/attendances/new', methods='post')
    @require_auth
    def post(request, session, form_data: dict):
        """Processa novo atendimento para uma vítima já cadastrada."""
        user = get_current_user(session)
        data = dict(form_data)

        victim_id = data.get('victim_id')
        if not victim_id:
            return Titled(
                "Vítima não informada",
                Main(
                    Div("Nenhuma vítima foi informada para o atendimento.", cls="alert alert-error"),
                    A("Voltar para lista de vítimas", href="/victims", cls="btn btn-primary"),
                    cls="container",
                ),
            )

        def parse_date(value):
            if not value:
                return None
            return datetime.strptime(value, '%Y-%m-%d').date()

        def parse_datetime(value):
            if not value:
                return None
            return datetime.strptime(value, '%Y-%m-%dT%H:%M')

        def parse_decimal(value):
            if not value:
                return None
            try:
                return float(value)
            except ValueError:
                return None

        # Criar atendimento vinculado à vítima existente
        attendance_data = {
            'victim_id': victim_id,
            'user_id': user['id'],
            'measure_number': data.get('measure_number'),
            'measure_start_date': parse_date(data.get('measure_start_date')),
            'measure_status': data.get('measure_status'),
            'visit_datetime': parse_datetime(data.get('visit_datetime')),
            'notes': data.get('notes'),
            'latitude': parse_decimal(data.get('latitude')),
            'longitude': parse_decimal(data.get('longitude')),
        }

        success_att, attendance_id = AttendanceService.create_attendance(attendance_data)

        if not success_att:
            return Titled(
                "Erro",
                Main(
                    Div(f"Erro ao cadastrar atendimento: {attendance_id}", cls="alert alert-error"),
                    A("Voltar para a vítima", href=f"/attendances/new?victim_id={victim_id}", cls="btn btn-primary"),
                    cls="container",
                ),
            )

        return RedirectResponse(f'/attendances/{attendance_id}', status_code=303)
    
    @rt('/attendances/{attendance_id}')
    @require_auth
    def get(request, session, attendance_id: str):
        """Visualiza detalhes do atendimento"""
        user = get_current_user(session)
        attendance = AttendanceService.get_attendance_by_id(attendance_id)
        
        if not attendance:
            return Titled(
                "Atendimento não encontrado",
                Main(
                    Div("Atendimento não encontrado", cls="alert alert-error"),
                    A("Voltar", href="/", cls="btn btn-primary"),
                    cls="container"
                )
            )
        
        # Formatar dados
        visit_date = attendance['visit_datetime'].strftime('%d/%m/%Y às %H:%M')
        birth_date = attendance['birth_date'].strftime('%d/%m/%Y')
        measure_date = attendance['measure_start_date'].strftime('%d/%m/%Y')
        
        # Endereço completo
        address_parts = []
        if attendance['address_type'] and attendance['address_name']:
            address_parts.append(f"{attendance['address_type']} {attendance['address_name']}")
        if attendance['address_number']:
            address_parts.append(f"nº {attendance['address_number']}")
        if attendance['address_complement']:
            address_parts.append(attendance['address_complement'])
        
        full_address = ", ".join(address_parts) if address_parts else "Não informado"
        
        location_parts = []
        if attendance['neighborhood']:
            location_parts.append(attendance['neighborhood'])
        if attendance['city']:
            location_parts.append(attendance['city'])
        if attendance['state']:
            location_parts.append(attendance['state'])
        
        full_location = " - ".join(location_parts) if location_parts else "Não informado"
        
        # Status da medida
        status_dict = dict(Config.MEASURE_STATUS)
        status_label = status_dict.get(attendance['measure_status'], attendance['measure_status'])
        
        # Mapa (se houver coordenadas)
        map_section = None
        if attendance['latitude'] and attendance['longitude']:
            map_url = f"https://www.google.com/maps?q={attendance['latitude']},{attendance['longitude']}"
            map_section = Fieldset(
                Legend("Localização"),
                Div(
                    P(f"Latitude: {attendance['latitude']}"),
                    P(f"Longitude: {attendance['longitude']}"),
                    A("Ver no Google Maps", href=map_url, target="_blank", cls="btn btn-secondary"),
                    cls="map-info"
                )
            )
        
        return Titled(
            f"Atendimento #{attendance_id}",
            Header(
                Div(
                    H1(f"Atendimento #{attendance_id}"),
                    P(f"{user['rank']} {user['name']}", cls="user-info"),
                    cls="header-content"
                ),
                Div(
                    A("Voltar", href="/", cls="btn btn-secondary"),
                    cls="header-actions"
                ),
                cls="main-header"
            ),
            Main(
                Div(
                    # Dados da Vítima
                    Fieldset(
                        Legend("Dados da Vítima"),
                        Dl(
                            Dt("Nome:"), Dd(attendance['victim_name']),
                            Dt("Data de Nascimento:"), Dd(birth_date),
                            Dt("CPF:"), Dd(attendance['cpf'] or "Não informado"),
                            Dt("Telefone:"), Dd(attendance['phone'] or "Não informado"),
                            Dt("Telefone Secundário:"), Dd(attendance['secondary_phone'] or "Não informado"),
                            cls="details-list"
                        )
                    ),
                    
                    # Endereço
                    Fieldset(
                        Legend("Endereço"),
                        Dl(
                            Dt("Endereço:"), Dd(full_address),
                            Dt("Localidade:"), Dd(full_location),
                            Dt("CEP:"), Dd(attendance['zip_code'] or "Não informado"),
                            cls="details-list"
                        )
                    ),
                    
                    # Medida Protetiva
                    Fieldset(
                        Legend("Medida Protetiva"),
                        Dl(
                            Dt("Número:"), Dd(attendance['measure_number']),
                            Dt("Data de Início:"), Dd(measure_date),
                            Dt("Situação:"), Dd(status_label),
                            cls="details-list"
                        )
                    ),
                    
                    # Atendimento
                    Fieldset(
                        Legend("Dados do Atendimento"),
                        Dl(
                            Dt("Data/Hora da Visita:"), Dd(visit_date),
                            Dt("Policial Responsável:"), Dd(f"{attendance['officer_rank']} {attendance['officer_name']}"),
                            Dt("Observações:"), Dd(attendance['notes'] or "Nenhuma observação registrada"),
                            cls="details-list"
                        )
                    ),
                    
                    # Mapa (se disponível)
                    map_section if map_section else None,
                    
                    cls="details-container"
                ),
                cls="container"
            )
        )