/**
 * Geolocation utilities for capturing and displaying location
 */

let currentPosition = null;
let geoRetryCount = 0;
const MAX_GEO_RETRIES = 1; // tenta mais 1 vez em caso de falha de precisão/timeout

/**
 * Captura a localização atual com alta precisão
 */
function captureLocation() {
    const statusDiv = document.getElementById('location-status');
    const captureBtn = document.getElementById('capture-btn');
    const mapBtn = document.getElementById('map-btn');
    
    // Verifica se o navegador suporta geolocalização
    if (!navigator.geolocation) {
        statusDiv.innerHTML = '<p class="error">Seu navegador não suporta geolocalização.</p>';
        return;
    }
    
    // Desabilita o botão durante a captura
    captureBtn.disabled = true;
    captureBtn.textContent = '📍 Capturando...';
    statusDiv.innerHTML = '<p class="info">Aguarde, capturando localização...</p>';

    geoRetryCount = 0;

    // Função de sucesso compartilhada
    function handleSuccess(position) {
        currentPosition = position;
        const lat = position.coords.latitude.toFixed(8);
        const lon = position.coords.longitude.toFixed(8);
        const accuracy = position.coords.accuracy.toFixed(2);

        // Preenche os campos
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lon;

        // Atualiza status
        statusDiv.innerHTML = `
            <p class="success">
                ✓ Localização capturada com sucesso!<br>
                Precisão: aproximadamente ${accuracy} metros
            </p>
        `;

        // Habilita botão de conferir no mapa
        mapBtn.style.display = 'inline-block';

        // Reabilita botão de captura
        captureBtn.disabled = false;
        captureBtn.textContent = '📍 Capturar Localização';
    }

    function handleError(error, triedFallback) {
        let errorMessage = '';

        // Em caso de timeout/posição indisponível, tenta uma segunda vez com configuração mais tolerante
        if (!triedFallback && geoRetryCount < MAX_GEO_RETRIES &&
            (error.code === error.TIMEOUT || error.code === error.POSITION_UNAVAILABLE)) {
            geoRetryCount++;
            statusDiv.innerHTML = '<p class="info">Tentando novamente obter a localização (modo alternativo)...</p>';

            const fallbackOptions = {
                enableHighAccuracy: true,   // mantém alta precisão sempre que possível
                timeout: 30000,            // aumenta timeout para 30s
                maximumAge: 5 * 60 * 1000  // aceita posição em cache até 5 minutos
            };

            navigator.geolocation.getCurrentPosition(
                handleSuccess,
                (err) => handleError(err, true),
                fallbackOptions,
            );
            return;
        }

        switch (error.code) {
            case error.PERMISSION_DENIED:
                errorMessage = 'Permissão negada. Por favor, permita o acesso à localização.';
                break;
            case error.POSITION_UNAVAILABLE:
                errorMessage = 'Localização indisponível. Verifique se o GPS está ativado.';
                break;
            case error.TIMEOUT:
                errorMessage = 'Tempo esgotado. Tente se aproximar de uma área aberta e tente novamente.';
                break;
            default:
                errorMessage = 'Erro desconhecido ao capturar localização.';
        }

        statusDiv.innerHTML = `<p class="error">✗ ${errorMessage}</p>`;
        captureBtn.disabled = false;
        captureBtn.textContent = '📍 Capturar Localização';
    }

    // Primeira tentativa: alta precisão, timeout maior e maior janela de cache
    const options = {
        enableHighAccuracy: true,       // Alta precisão
        timeout: 20000,                 // Timeout de 20 segundos
        maximumAge: 2 * 60 * 1000       // Aceita posição recente de até 2 minutos
    };

    navigator.geolocation.getCurrentPosition(
        handleSuccess,
        (error) => handleError(error, false),
        options,
    );
}

/**
 * Abre o Google Maps com as coordenadas capturadas
 */
function checkOnMap() {
    const lat = document.getElementById('latitude').value;
    const lon = document.getElementById('longitude').value;
    
    if (!lat || !lon) {
        alert('Por favor, capture a localização primeiro.');
        return;
    }
    
    // Abre Google Maps em nova aba
    const mapUrl = `https://www.google.com/maps?q=${lat},${lon}`;
    window.open(mapUrl, '_blank');
}

/**
 * Monitora mudanças manuais nos campos de latitude/longitude
 */
document.addEventListener('DOMContentLoaded', function() {
    const latInput = document.getElementById('latitude');
    const lonInput = document.getElementById('longitude');
    const mapBtn = document.getElementById('map-btn');
    
    if (latInput && lonInput && mapBtn) {
        // Mostra botão de mapa se houver coordenadas
        function checkCoordinates() {
            if (latInput.value && lonInput.value) {
                mapBtn.style.display = 'inline-block';
            } else {
                mapBtn.style.display = 'none';
            }
        }
        
        latInput.addEventListener('input', checkCoordinates);
        lonInput.addEventListener('input', checkCoordinates);
        
        // Verifica ao carregar a página
        checkCoordinates();
    }
});