const btnHablar = document.getElementById('btn-hablar');
const chatBox = document.getElementById('chat-box');
const iconMic = document.getElementById('icon-mic');
const textInput = document.getElementById('text-input');
const btnEnviarTexto = document.getElementById('btn-enviar-texto');

// Elementos para la transición de interfaz
const welcomeArea = document.getElementById('welcome-area');
const chatContainer = document.getElementById('chat-container');
const theInputBox = document.getElementById('the-input-box');
const bottomInputContainer = document.getElementById('bottom-input-container');

// Configuración de Voz
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const reconocimiento = new SpeechRecognition();
reconocimiento.lang = 'es-ES';
reconocimiento.interimResults = true;
reconocimiento.continuous = true;

// Generar un ID único para esta sesión de chat
const sessionID = "usuario_" + Math.random().toString(36).substring(2, 10);

// --- CONFIGURACIÓN DE VOZ NATIVA (ACENTO LATINO Y MÁS FLUIDA) ---
function reproducirVozFemenina(texto) {
    // Si Consultina estaba hablando, la callamos antes de iniciar el nuevo audio
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }

    const mensajeVoz = new SpeechSynthesisUtterance(texto);
    
    // Configuramos el idioma a Español Latinoamericano / Neutral
    mensajeVoz.lang = 'es-MX'; // México / Latino neutral
    
    // Ajustes de fluidez (Más naturales, menos robóticos)
    mensajeVoz.rate = 1.0;     // Velocidad normal para que articule bien las palabras
    mensajeVoz.pitch = 1.05;   // Tono muy ligeramente agudo (femenino) sin distorsionar

    // Buscar la lista de voces instaladas en la computadora/navegador
    const voces = window.speechSynthesis.getVoices();
    
    // Filtro avanzado: Buscamos nombres específicos de voces femeninas LATINOAMERICANAS
    let vozSeleccionada = voces.find(voz => 
        (voz.lang.includes('es-MX') || voz.lang.includes('es-US') || voz.lang.includes('es-419') || voz.lang.includes('es')) && 
        (
            voz.name.includes('Sabina') ||           // Microsoft (Windows - Español México)
            voz.name.includes('Paulina') ||          // Mac / iOS (Español México)
            voz.name.includes('Mia') ||              // Mac / iOS (Español México)
            voz.name.includes('Google español de Estados Unidos') || // Chrome / Android (Neutral Femenino)
            voz.name.includes('Google Español')      // Chrome genérico
        ) && 
        !voz.name.includes('Helena') && !voz.name.includes('Laura') // Excluimos explícitamente los acentos de España
    );

    // Fallback 1: Si no tiene esos nombres exactos, agarramos cualquier voz de México o US (Latino)
    if (!vozSeleccionada) {
        vozSeleccionada = voces.find(voz => voz.lang.includes('es-MX') || voz.lang.includes('es-US') || voz.lang.includes('es-419'));
    }

    // Fallback 2: Último recurso, la primera en español que encuentre
    if (!vozSeleccionada) {
        vozSeleccionada = voces.find(voz => voz.lang.includes('es'));
    }

    // Le asignamos la voz femenina al mensaje
    if (vozSeleccionada) {
        mensajeVoz.voice = vozSeleccionada;
    }

    // Le damos play a la voz
    window.speechSynthesis.speak(mensajeVoz);
}
// ------------------------------------------------

let escuchando = false;
let chatIniciado = false;
let textoEscuchado = "";

// 1. Función clave: Transición de "Pantalla Vacía" a "Modo Chat"
function transicionAChat() {
    if (chatIniciado) return;
    chatIniciado = true;

    welcomeArea.classList.add('hidden');
    chatContainer.classList.remove('hidden');
    chatContainer.classList.add('flex');

    bottomInputContainer.appendChild(theInputBox);
}

// 2. Función para renderizar los mensajes
function agregarMensaje(remitente, texto, esUsuario) {
    if (!chatIniciado) transicionAChat();

    const div = document.createElement('div');
    div.className = `flex w-full opacity-0 animate-[fadeIn_0.4s_ease-out_forwards] ${esUsuario ? "justify-end" : "justify-start"}`;

    let htmlContent = '';

    if (esUsuario) {
        htmlContent = `
            <div class="bg-primary text-white shadow-md px-5 py-3.5 rounded-3xl rounded-br-sm max-w-[85%] md:max-w-[70%] text-[15px] font-medium leading-relaxed tracking-wide shadow-primary/20">
                ${texto}
            </div>
        `;
    } else {
        htmlContent = `
            <div class="flex gap-4 w-full md:max-w-[85%]">
                <div class="w-9 h-9 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <img src="assets/images/Logo.png" alt="Avatar Consultina" class="w-full h-full object-contain drop-shadow-sm">
                </div>
                <div class="bg-white border border-gray-100 shadow-sm rounded-3xl rounded-tl-sm px-6 py-4 text-gray-800 text-[15px] leading-relaxed w-full">
                    ${texto}
                </div>
            </div>
        `;
    }

    div.innerHTML = htmlContent;
    chatBox.appendChild(div);

    setTimeout(() => {
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    }, 50);
}

// 3. Control del micrófono
btnHablar.onclick = () => {
    // Si el usuario toca el micrófono, interrumpimos a Consultina
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }

    if (!escuchando) {
        try { reconocimiento.start(); } catch (e) { }
    } else {
        reconocimiento.stop();
    }
};

// 4. Estados visuales al escuchar
reconocimiento.onstart = () => {
    if (!chatIniciado) transicionAChat();
    escuchando = true;
    textoEscuchado = "";
    textInput.value = "";

    theInputBox.classList.add('escuchando-fx', 'bg-white');
    theInputBox.classList.remove('bg-inputBg');

    btnHablar.classList.add('bg-primary', 'text-white');
    btnHablar.classList.remove('bg-transparent', 'text-gray-600', 'hover:bg-gray-200');

    btnHablar.classList.remove('hidden');
    btnEnviarTexto.classList.add('hidden');

    textInput.placeholder = 'Te escucho (Haz clic de nuevo en el micrófono para enviar)...';

    iconMic.innerHTML = '<rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect>';
};

// 5. Mostrar texto en tiempo real y preparar el envío
reconocimiento.onresult = (event) => {
    let transcripcionInterina = '';
    textoEscuchado = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
            textoEscuchado += event.results[i][0].transcript + ' ';
        } else {
            transcripcionInterina += event.results[i][0].transcript;
        }
    }

    textInput.value = textoEscuchado + transcripcionInterina;
};

// 6. Al apagar el micrófono, se corrige y se envía el texto
reconocimiento.onend = () => {
    escuchando = false;

    theInputBox.classList.remove('escuchando-fx', 'bg-white');
    theInputBox.classList.add('bg-inputBg');
    btnHablar.classList.remove('bg-primary', 'text-white');
    btnHablar.classList.add('bg-transparent', 'text-gray-600', 'hover:bg-gray-200');
    textInput.placeholder = 'Consultina está analizando...';
    iconMic.innerHTML = '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" x2="12" y1="19" y2="22"></line>';

    let textoFinal = textInput.value.trim();

    if (textoFinal.length > 0) {
        textoFinal = textoFinal.replace(/consultiva/gi, "Consultina");
        textoFinal = textoFinal.replace(/con dulcina/gi, "Consultina");
        textoFinal = textoFinal.replace(/concertina/gi, "Consultina");
        textoFinal = textoFinal.replace(/consulta/gi, "Consultina");
        textoFinal = textoFinal.replace(/consultena/gi, "Consultina");
        textoFinal = textoFinal.replace(/mancillar/gi, "mención");
        textoFinal = textoFinal.replace(/medición/gi, "mención");

        textInput.value = "";
        enviarMensajeServidor(textoFinal);
    } else {
        textInput.placeholder = 'Escribe o habla tu pregunta a Consultina...';
    }
};

reconocimiento.onerror = () => {
    textInput.placeholder = 'Escribe o habla tu pregunta a Consultina...';
};

// 7. Lógica de Input de Texto
textInput.addEventListener('input', () => {
    if (escuchando) return;

    if (textInput.value.trim().length > 0) {
        btnHablar.classList.add('hidden');
        btnEnviarTexto.classList.remove('hidden');
    } else {
        btnHablar.classList.remove('hidden');
        btnEnviarTexto.classList.add('hidden');
    }
});

textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        enviarTextoLibre();
    }
});

btnEnviarTexto.onclick = () => {
    enviarTextoLibre();
};

// --- FUNCIONES DE ANIMACIÓN "PENSANDO" ---
function mostrarCargando() {
    if (!chatIniciado) transicionAChat();
    
    if (document.getElementById('mensaje-cargando')) return;

    const divCargando = document.createElement('div');
    divCargando.id = 'mensaje-cargando';
    // 🚨 ELIMINAMOS EL RETRASO: Ahora aparece instantáneamente de golpe
    divCargando.className = `flex w-full justify-start mt-2 mb-2`; 
    
    divCargando.innerHTML = `
        <div class="flex gap-4 w-full md:max-w-[85%]">
            <div class="w-9 h-9 flex items-center justify-center flex-shrink-0 mt-0.5">
                <img src="assets/images/Logo.png" alt="Avatar Consultina" class="w-full h-full object-contain drop-shadow-sm">
            </div>
            <div class="bg-white border border-gray-100 shadow-sm rounded-3xl rounded-tl-sm px-5 py-4 w-auto flex items-center justify-center min-w-[70px] min-h-[45px]">
                <div class="flex space-x-1.5">
                    <div class="w-2.5 h-2.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0s;"></div>
                    <div class="w-2.5 h-2.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.15s;"></div>
                    <div class="w-2.5 h-2.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.3s;"></div>
                </div>
            </div>
        </div>
    `;
    
    chatBox.appendChild(divCargando);
    
    setTimeout(() => {
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    }, 10);
}

function ocultarCargando() {
    const divCargando = document.getElementById('mensaje-cargando');
    if (divCargando) {
        divCargando.remove();
    }
}
// ----------------------------------------

function enviarTextoLibre() {
    const textoUsuario = textInput.value.trim();
    if (textoUsuario === '') return;

    textInput.value = '';
    btnHablar.classList.remove('hidden');
    btnEnviarTexto.classList.add('hidden');

    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }

    enviarMensajeServidor(textoUsuario);
}

// 8. Comunicación con Rasa
async function enviarMensajeServidor(textoUsuario) {
    agregarMensaje("Tú", textoUsuario, true);
    textInput.placeholder = 'Consultina está analizando...';
    textInput.disabled = true;

    // 1. Mostrar la burbuja de los 3 puntitos INSTANTÁNEAMENTE
    mostrarCargando();

    // 2. Darle un micro-respiro al navegador (50ms) para que dibuje los puntitos en pantalla
    setTimeout(async () => {
        try {
            const respuesta = await fetch("http://localhost:5005/webhooks/rest/webhook", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sender: sessionID, message: textoUsuario })
            });

            const data = await respuesta.json();
            
            // 3. Ya llegó la respuesta, ocultamos los puntitos
            ocultarCargando();
            
            if(data && data.length > 0) {
                let textoParaVoz = "";
                let textoParaChat = "";
                
                data.forEach((mensaje, index) => {
                    if (index > 0 && (mensaje.text || mensaje.image)) {
                        textoParaChat += '<br><br>'; 
                    }
                    
                    if(mensaje.text) {
                        let textoCapa = mensaje.text
                            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-primary font-semibold">$1</strong>')
                            .replace(/\n/g, '<br>');
                        
                        textoParaChat += textoCapa;
                        
                        let elementoTemporal = document.createElement("div");
                        elementoTemporal.innerHTML = mensaje.text;
                        let textoSinCodigo = elementoTemporal.textContent || elementoTemporal.innerText || "";

                        let textoLimpioVoz = textoSinCodigo.replace(/\*/g, '');
                        textoLimpioVoz = textoLimpioVoz.replace(/NVIDIA/g, 'Envidia');
                        textoLimpioVoz = textoLimpioVoz.replace(/USFQ/g, 'U S F Q');
                        textoLimpioVoz = textoLimpioVoz.replace(/UDLA/g, 'Udla');
                        textoLimpioVoz = textoLimpioVoz.replace(/IESS/g, 'Íes');
                        textoLimpioVoz = textoLimpioVoz.replace(/MSP/g, 'Eme Ese Pe');
                        textoLimpioVoz = textoLimpioVoz.replace(/CGE/g, 'C G E');
                        textoLimpioVoz = textoLimpioVoz.replace(/\$([0-9]+)\.([0-9]+)/g, '$1 dólares con $2 centavos');
                        textoLimpioVoz = textoLimpioVoz.replace(/\$([0-9]+)/g, '$1 dólares');
                        
                        textoParaVoz += textoLimpioVoz + ". ";
                    }
                    
                    if(mensaje.image) {
                        let imgCapa = `<img src="${mensaje.image}" alt="Imagen adjunta" class="w-64 md:w-72 h-auto rounded-xl mt-3 shadow-sm border border-gray-100">`;
                        textoParaChat += imgCapa;
                    }
                });
                
                if(textoParaChat.trim().length > 0) {
                    agregarMensaje("Consultina", textoParaChat, false);
                }
                
                if(textoParaVoz.trim().length > 0) {
                    reproducirVozFemenina(textoParaVoz);
                }
            }
        } catch (error) {
            ocultarCargando();
            agregarMensaje("Sistema", "Error de conexión con el servidor de IA.", false);
        } finally {
            textInput.placeholder = 'Escribe o habla tu pregunta a Consultina...';
            textInput.disabled = false;
            textInput.focus();
        }
    }); 

}