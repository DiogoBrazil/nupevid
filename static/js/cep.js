/**
 * CEP lookup using BrasilAPI
 */

/**
 * Formata o CEP enquanto digita
 */
function formatCEP(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length > 8) {
        value = value.substring(0, 8);
    }
    
    if (value.length > 5) {
        value = value.substring(0, 5) + '-' + value.substring(5);
    }
    
    input.value = value;
}

/**
 * Busca dados do CEP na API
 */
async function buscarCEP() {
    const cepInput = document.getElementById('zip_code');
    const cep = cepInput.value.replace(/\D/g, '');
    
    // Valida CEP
    if (cep.length !== 8) {
        alert('Por favor, informe um CEP válido com 8 dígitos.');
        cepInput.focus();
        return;
    }
    
    // Mostra loading
    const originalText = event.target.textContent;
    event.target.textContent = 'Buscando...';
    event.target.disabled = true;
    
    try {
        // Usa BrasilAPI (gratuita e sem necessidade de chave)
        const response = await fetch(`https://brasilapi.com.br/api/cep/v1/${cep}`);
        
        if (!response.ok) {
            throw new Error('CEP não encontrado');
        }
        
        const data = await response.json();
        
        // Preenche os campos
        if (data.street) {
            // Tenta separar tipo e nome da rua
            const streetParts = data.street.split(' ', 1);
            const addressType = streetParts[0];
            const addressName = data.street.substring(streetParts[0].length).trim();
            
            // Lista de tipos válidos
            const validTypes = ['Rua', 'Avenida', 'Travessa', 'Alameda', 'Praça', 
                              'Rodovia', 'Estrada', 'Via', 'Beco', 'Largo'];
            
            if (validTypes.includes(addressType)) {
                document.getElementById('address_type').value = addressType;
                document.getElementById('address_name').value = addressName;
            } else {
                document.getElementById('address_name').value = data.street;
            }
        }
        
        if (data.neighborhood) {
            document.getElementById('neighborhood').value = data.neighborhood;
        }
        
        if (data.city) {
            document.getElementById('city').value = data.city;
        }
        
        if (data.state) {
            document.getElementById('state').value = data.state;
        }
        
        // Foca no campo de número
        document.getElementById('address_number').focus();
        
        alert('CEP encontrado! Confira os dados preenchidos.');
        
    } catch (error) {
        alert('CEP não encontrado. Você pode preencher o endereço manualmente.');
        console.error('Erro ao buscar CEP:', error);
    } finally {
        event.target.textContent = originalText;
        event.target.disabled = false;
    }
}

/**
 * Adiciona formatação automática ao campo CEP
 */
document.addEventListener('DOMContentLoaded', function() {
    const cepInput = document.getElementById('zip_code');
    
    if (cepInput) {
        cepInput.addEventListener('input', function() {
            formatCEP(this);
        });
        
        // Permite buscar CEP ao pressionar Enter
        cepInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                buscarCEP();
            }
        });
    }
    
    // Formata CPF enquanto digita
    const cpfInput = document.getElementById('cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            
            if (value.length > 11) {
                value = value.substring(0, 11);
            }
            
            if (value.length > 9) {
                value = value.substring(0, 3) + '.' + 
                        value.substring(3, 6) + '.' + 
                        value.substring(6, 9) + '-' + 
                        value.substring(9);
            } else if (value.length > 6) {
                value = value.substring(0, 3) + '.' + 
                        value.substring(3, 6) + '.' + 
                        value.substring(6);
            } else if (value.length > 3) {
                value = value.substring(0, 3) + '.' + value.substring(3);
            }
            
            this.value = value;
        });
    }
    
    // Formata telefone enquanto digita
    function formatPhone(input) {
        let value = input.value.replace(/\D/g, '');
        
        if (value.length > 11) {
            value = value.substring(0, 11);
        }
        
        if (value.length > 10) {
            value = '(' + value.substring(0, 2) + ') ' + 
                    value.substring(2, 7) + '-' + 
                    value.substring(7);
        } else if (value.length > 6) {
            value = '(' + value.substring(0, 2) + ') ' + 
                    value.substring(2, 6) + '-' + 
                    value.substring(6);
        } else if (value.length > 2) {
            value = '(' + value.substring(0, 2) + ') ' + value.substring(2);
        }
        
        input.value = value;
    }
    
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            formatPhone(this);
        });
    }
    
    const secondaryPhoneInput = document.getElementById('secondary_phone');
    if (secondaryPhoneInput) {
        secondaryPhoneInput.addEventListener('input', function() {
            formatPhone(this);
        });
    }
});