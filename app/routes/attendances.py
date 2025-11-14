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
                A("Novo Atendimento", href="/attendances/new", cls="btn btn-primary"),
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
                            A("Ver Detalhes", href=f"/attendances/{att['id']}", cls="btn btn-sm"),
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
                A("Cadastrar primeiro atendimento", href="/attendances/new", cls="btn btn-primary"),
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
    def get(request, session):
        """Formulário de novo atendimento"""
        user = get_current_user(session)
        
        address_type_options = [
            Option(addr_type, value=addr_type) 
            for addr_type in Config.ADDRESS_TYPES
        ]
        
        state_options = [
            Option(state, value=state, selected=(state == 'RO'))
            for state in Config.BRAZILIAN_STATES
        ]
        
        status_options = [
            Option(label, value=value)
            for value, label in Config.MEASURE_STATUS
        ]
        
        return Titled(
            "Novo Atendimento - Patrulha Maria da Penha",
            Header(
                Div(
                    H1("Novo Atendimento"),
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
                Form(
                    # Seção: Dados da Vítima
                    Fieldset(
                        Legend("Dados da Vítima"),
                        Div(
                            Div(
                                Label("Nome Completo *", _for="full_name"),
                                Input(
                                    type="text",
                                    id="full_name",
                                    name="full_name",
                                    required=True,
                                    placeholder="Maria da Silva"
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Data de Nascimento *", _for="birth_date"),
                                Input(
                                    type="date",
                                    id="birth_date",
                                    name="birth_date",
                                    required=True
                                ),
                                cls="form-group"
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Div(
                                Label("CPF", _for="cpf"),
                                Input(
                                    type="text",
                                    id="cpf",
                                    name="cpf",
                                    placeholder="000.000.000-00",
                                    maxlength="14"
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Telefone Principal", _for="phone"),
                                Input(
                                    type="tel",
                                    id="phone",
                                    name="phone",
                                    placeholder="(69) 99999-9999"
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Telefone Secundário", _for="secondary_phone"),
                                Input(
                                    type="tel",
                                    id="secondary_phone",
                                    name="secondary_phone",
                                    placeholder="(69) 99999-9999"
                                ),
                                cls="form-group"
                            ),
                            cls="form-row"
                        )
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
                                        maxlength="9"
                                    ),
                                    Button(
                                        "Buscar CEP",
                                        type="button",
                                        onclick="buscarCEP()",
                                        cls="btn btn-sm"
                                    ),
                                    cls="input-group"
                                ),
                                Small("Opcional - pode preencher manualmente", cls="help-text"),
                                cls="form-group"
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Div(
                                Label("Tipo de Logradouro", _for="address_type"),
                                Select(
                                    *address_type_options,
                                    id="address_type",
                                    name="address_type"
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Nome do Logradouro", _for="address_name"),
                                Input(
                                    type="text",
                                    id="address_name",
                                    name="address_name",
                                    placeholder="das Flores"
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Número", _for="address_number"),
                                Input(
                                    type="text",
                                    id="address_number",
                                    name="address_number",
                                    placeholder="123"
                                ),
                                cls="form-group"
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Div(
                                Label("Bairro", _for="neighborhood"),
                                Input(
                                    type="text",
                                    id="neighborhood",
                                    name="neighborhood",
                                    placeholder="Centro"
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Cidade", _for="city"),
                                Input(
                                    type="text",
                                    id="city",
                                    name="city",
                                    placeholder="Porto Velho"
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Estado", _for="state"),
                                Select(
                                    *state_options,
                                    id="state",
                                    name="state"
                                ),
                                cls="form-group"
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Div(
                                Label("Complemento", _for="address_complement"),
                                Input(
                                    type="text",
                                    id="address_complement",
                                    name="address_complement",
                                    placeholder="Apto 201, Bloco B"
                                ),
                                cls="form-group"
                            ),
                            cls="form-row"
                        )
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
                                    placeholder="0000000-00.0000.0.00.0000"
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Data de Início *", _for="measure_start_date"),
                                Input(
                                    type="date",
                                    id="measure_start_date",
                                    name="measure_start_date",
                                    required=True
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Situação *", _for="measure_status"),
                                Select(
                                    *status_options,
                                    id="measure_status",
                                    name="measure_status",
                                    required=True
                                ),
                                cls="form-group"
                            ),
                            cls="form-row"
                        )
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
                                    value=datetime.now().strftime('%Y-%m-%dT%H:%M')
                                ),
                                cls="form-group"
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Div(
                                Label("Observações", _for="notes"),
                                Textarea(
                                    id="notes",
                                    name="notes",
                                    rows="4",
                                    placeholder="Descreva detalhes da visita, situação encontrada, etc."
                                ),
                                cls="form-group"
                            ),
                            cls="form-row"
                        )
                    ),
                    
                    # Seção: Geolocalização
                    Fieldset(
                        Legend("Geolocalização (Opcional)"),
                        Div(
                            P("A coleta de localização é opcional, mas ajuda em análises futuras."),
                            cls="info-message"
                        ),
                        Div(
                            Div(
                                Label("Latitude", _for="latitude"),
                                Input(
                                    type="text",
                                    id="latitude",
                                    name="latitude",
                                    placeholder="-8.7612",
                                    readonly=True
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Label("Longitude", _for="longitude"),
                                Input(
                                    type="text",
                                    id="longitude",
                                    name="longitude",
                                    placeholder="-63.9004",
                                    readonly=True
                                ),
                                cls="form-group"
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Button(
                                "📍 Capturar Localização",
                                type="button",
                                onclick="captureLocation()",
                                cls="btn btn-secondary",
                                id="capture-btn"
                            ),
                            Button(
                                "🗺️ Conferir no Mapa",
                                type="button",
                                onclick="checkOnMap()",
                                cls="btn btn-secondary",
                                id="map-btn",
                                style="display:none;"
                            ),
                            cls="button-group"
                        ),
                        Div(id="location-status", cls="status-message")
                    ),
                    
                    # Botões de ação
                    Div(
                        Button("Salvar Atendimento", type="submit", cls="btn btn-primary"),
                        A("Cancelar", href="/", cls="btn btn-secondary"),
                        cls="button-group form-actions"
                    ),
                    
                    method="post",
                    action="/attendances/new"
                ),
                cls="container form-container"
            ),
            Script(src="/static/js/geolocation.js"),
            Script(src="/static/js/cep.js")
        )
    
    @rt('/attendances/new', methods='post')
    @require_auth
    def post(request, session, form_data: dict):
        """Processa novo atendimento"""
        user = get_current_user(session)
        form_data = dict(form_data)

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
        
        # Criar vítima
        victim_data = {
            'full_name': form_data.get('full_name'),
            'birth_date': parse_date(form_data.get('birth_date')),
            'cpf': form_data.get('cpf'),
            'phone': form_data.get('phone'),
            'secondary_phone': form_data.get('secondary_phone'),
            'address_type': form_data.get('address_type'),
            'address_name': form_data.get('address_name'),
            'address_number': form_data.get('address_number'),
            'address_complement': form_data.get('address_complement'),
            'neighborhood': form_data.get('neighborhood'),
            'city': form_data.get('city'),
            'state': form_data.get('state'),
            'zip_code': form_data.get('zip_code')
        }
        
        success_victim, victim_id = VictimService.create_victim(victim_data)
        
        if not success_victim:
            return Titled(
                "Erro",
                Main(
                    Div(f"Erro ao cadastrar vítima: {victim_id}", cls="alert alert-error"),
                    A("Voltar", href="/attendances/new", cls="btn btn-primary"),
                    cls="container"
                )
            )
        
        # Criar atendimento
        attendance_data = {
            'victim_id': victim_id,
            'user_id': user['id'],
            'measure_number': form_data.get('measure_number'),
            'measure_start_date': parse_date(form_data.get('measure_start_date')),
            'measure_status': form_data.get('measure_status'),
            'visit_datetime': parse_datetime(form_data.get('visit_datetime')),
            'notes': form_data.get('notes'),
            'latitude': parse_decimal(form_data.get('latitude')),
            'longitude': parse_decimal(form_data.get('longitude'))
        }
        
        success_att, attendance_id = AttendanceService.create_attendance(attendance_data)
        
        if not success_att:
            return Titled(
                "Erro",
                Main(
                    Div(f"Erro ao cadastrar atendimento: {attendance_id}", cls="alert alert-error"),
                    A("Voltar", href="/attendances/new", cls="btn btn-primary"),
                    cls="container"
                )
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