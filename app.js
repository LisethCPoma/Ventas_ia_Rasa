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
reconocimiento.interimResults = false;

// --- CONFIGURACIÓN DE VOZ FEMENINA Y NATURAL ---
// Variable global para almacenar las voces una vez cargadas
let vocesDisponibles = [];

function cargarVoces() {
    vocesDisponibles = window.speechSynthesis.getVoices();
}
// Escuchar cuando las voces se carguen en el navegador
if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = cargarVoces;
}
cargarVoces();

// Función dedicada para hablar con voz femenina asegurada
function reproducirVozFemenina(texto) {
    // Es importante crear un nuevo Onbjeto Utterance justo antes de hablar en Chrome 
    // porque los globales a veces pierden sus propiedades o fallan
    const nuevaVoz = new SpeechSynthesisUtterance(texto);
    nuevaVoz.lang = 'es-ES';
    nuevaVoz.rate = 1.0; 
    nuevaVoz.pitch = 1.0;

    let voces = vocesDisponibles.length > 0 ? vocesDisponibles : window.speechSynthesis.getVoices();
    let vocesEsp = voces.filter(v => v.lang.includes('es'));

    // Lista de nombres femeninos conocidos en Mac y Chrome
    const nombresFemeninos = ['Monica', 'Paulina', 'Google español de Estados Unidos', 'Helena', 'Laura', 'Sabina', 'Victoria', 'Monica'];
    
    let vozInstanciada = null;
    
    // Buscar coincidencia exacta por ese orden de prioridad
    for (const nombre of nombresFemeninos) {
        vozInstanciada = vocesEsp.find(v => v.name.includes(nombre));
        if (vozInstanciada) break;
    }

    // Si detectamos en su lugar a voces masculinas conocidas en mac/chrome, las evitamos
    if (!vozInstanciada && vocesEsp.length > 0) {
        vozInstanciada = vocesEsp.find(v => 
            !v.name.includes('Jorge') && 
            !v.name.includes('Diego') && 
            !v.name.includes('Javier')
        );
        if (!vozInstanciada) {
            vozInstanciada = vocesEsp[0]; // Último recurso absoluto
        }
    }

    if (vozInstanciada) {
        nuevaVoz.voice = vozInstanciada;
    }

    // Cancelar cualquier discurso actual para prevenir solapamiento o bloqueos robóticos
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(nuevaVoz);
}
// ------------------------------------------------

let escuchando = false;
let chatIniciado = false;

// 1. Función clave: Transición de "Pantalla Vacía" a "Modo Chat"
function transicionAChat() {
    if (chatIniciado) return;
    chatIniciado = true;

    // Ocultar bienvenida, mostrar contenedor de chat
    welcomeArea.classList.add('hidden');
    chatContainer.classList.remove('hidden');
    chatContainer.classList.add('flex');
    
    // Mover dinámicamente el cuadro de entrada a la zona inferior
    bottomInputContainer.appendChild(theInputBox);
}

// 2. Función para renderizar los mensajes
function agregarMensaje(remitente, texto, esUsuario) {
    if (!chatIniciado) transicionAChat();

    const div = document.createElement('div');
    div.className = `flex w-full opacity-0 animate-[fadeIn_0.4s_ease-out_forwards] ${esUsuario ? "justify-end" : "justify-start"}`;

    let htmlContent = '';
    
    if (esUsuario) {
        // Estilo Usuario: Burbuja azul corporativa a la derecha
        htmlContent = `
            <div class="bg-primary text-white shadow-md px-5 py-3.5 rounded-3xl rounded-br-sm max-w-[85%] md:max-w-[70%] text-[15px] font-medium leading-relaxed tracking-wide shadow-primary/20">
                ${texto}
            </div>
        `;
    } else {
        // Estilo Consultina: Tarjeta limpia y moderna a la izquierda
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
    
    // Auto-scroll suave
    setTimeout(() => {
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    }, 50);
}

// 3. Control del micrófono
btnHablar.onclick = () => {
    // Si la agente está hablando y el usuario la interrumpe presionando el micrófono, silenciar inmediatamente
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }

    if (!escuchando) {
        try { reconocimiento.start(); } catch(e) {}
    } else {
        reconocimiento.stop();
    }
};

// 4. Estados visuales al escuchar
reconocimiento.onstart = () => {
    if (!chatIniciado) transicionAChat();
    escuchando = true;
    
    // Cambiar Input a estilo "Activo"
    theInputBox.classList.add('escuchando-fx', 'bg-white');
    theInputBox.classList.remove('bg-inputBg');
    
    // Botón azul corporativo
    btnHablar.classList.add('bg-primary', 'text-white');
    btnHablar.classList.remove('bg-transparent', 'text-gray-600', 'hover:bg-gray-200');
    
    textInput.placeholder = 'Te estoy escuchando...';
    
    // Ícono de Stop
    iconMic.innerHTML = '<rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect>';
};

reconocimiento.onend = () => {
    escuchando = false;
    
    // Restaurar Input
    theInputBox.classList.remove('escuchando-fx', 'bg-white');
    theInputBox.classList.add('bg-inputBg');
    
    // Restaurar Botón
    btnHablar.classList.remove('bg-primary', 'text-white');
    btnHablar.classList.add('bg-transparent', 'text-gray-600', 'hover:bg-gray-200');
    
    textInput.placeholder = 'Consultina está analizando...';
    
    // Ícono de Micrófono
    iconMic.innerHTML = '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" x2="12" y1="19" y2="22"></line>';
};

reconocimiento.onerror = () => {
    textInput.placeholder = 'Escribe o habla tu pregunta a Consultina...';
};

// 6. Lógica de Input de Texto
textInput.addEventListener('input', () => {
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

function enviarTextoLibre() {
    const textoUsuario = textInput.value.trim();
    if (textoUsuario === '') return;
    
    textInput.value = '';
    btnHablar.classList.remove('hidden');
    btnEnviarTexto.classList.add('hidden');
    
    // Si la agente está hablando, silenciar
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }
    
    enviarMensajeServidor(textoUsuario);
}

// 5. Enviar a Rasa y leer respuesta (Común para voz y texto)
reconocimiento.onresult = (event) => {
    const textoUsuario = event.results[0][0].transcript;
    enviarMensajeServidor(textoUsuario);
};

async function enviarMensajeServidor(textoUsuario) {
    agregarMensaje("Tú", textoUsuario, true);
    textInput.placeholder = 'Consultina está analizando...';
    textInput.disabled = true;

    try {
        const respuesta = await fetch("http://localhost:5005/webhooks/rest/webhook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sender: "usuario_demo", message: textoUsuario })
        });

        const data = await respuesta.json();
        
        if(data && data.length > 0) {
            let textoParaVoz = "";
            let textoParaChat = "";
            
            data.forEach((mensaje, index) => {
                // Si no es el primer mensaje, agregar un salto de párrafo
                if (index > 0 && (mensaje.text || mensaje.image)) {
                    textoParaChat += '<br><br>'; 
                }
                
                if(mensaje.text) {
                    let textoCapa = mensaje.text
                        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-primary font-semibold">$1</strong>')
                        .replace(/\n/g, '<br>');
                    
                    textoParaChat += textoCapa;
                    
                    textoParaVoz += mensaje.text.replace(/\*/g, '') + ". ";
                }
                
                if(mensaje.image) {
                    let imgCapa = `<img src="${mensaje.image}" alt="Imagen adjunta" class="max-w-full h-auto rounded-xl mt-3 shadow-sm border border-gray-100">`;
                    // Si ya había texto en este iterador, damos un margin top extra asegurando espacio
                    textoParaChat += imgCapa;
                }
            });
            
            // Inyectar una sola tarjeta al DOM unificada
            if(textoParaChat.trim().length > 0) {
                agregarMensaje("Consultina", textoParaChat, false);
            }
            
            // Hablar toda la cadena consolidada
            if(textoParaVoz.trim().length > 0) {
                reproducirVozFemenina(textoParaVoz);
            }
        }
    } catch (error) {
        agregarMensaje("Sistema", "Error de conexión con el servidor de IA.", false);
    } finally {
        textInput.placeholder = 'Escribe o habla tu pregunta a Consultina...';
        textInput.disabled = false;
        textInput.focus();
    }
}