const btnHablar = document.getElementById('btn-hablar');
const chatBox = document.getElementById('chat-box');
const statusText = document.getElementById('status-text');
const iconMic = document.getElementById('icon-mic');

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

const voz = new SpeechSynthesisUtterance();
voz.lang = 'es-ES';
voz.rate = 1.0; // Velocidad normal (1.0) suele sonar más natural
voz.pitch = 1.0; // Tono normal (1.0) evita el efecto robótico/ardilla

// --- CONFIGURACIÓN DE VOZ FEMENINA Y NATURAL ---
function configurarVozFemenina() {
    const voces = window.speechSynthesis.getVoices();
    // Filtramos voces que sean en español (España, México, Latinoamérica, etc.)
    const vocesEsp = voces.filter(v => v.lang.startsWith('es'));
    
    // Buscamos nombres de voces femeninas conocidas por ser de mejor calidad
    // Ej: "Google español" (Chrome/Android), "Microsoft Helena/Sabina/Laura" (Windows), "Monica/Paulina/Victoria" (macOS/iOS)
    let vozSeleccionada = vocesEsp.find(v => 
        v.name.includes('Google') || 
        v.name.includes('Helena') || 
        v.name.includes('Laura') || 
        v.name.includes('Sabina') || 
        v.name.includes('Paulina') || 
        v.name.includes('Monica') || 
        v.name.includes('Victoria')
    );

    // Si no encuentra las específicas, selecciona la primera en español
    if (!vozSeleccionada && vocesEsp.length > 0) {
        vozSeleccionada = vocesEsp[0];
    }
    
    if (vozSeleccionada) {
        voz.voice = vozSeleccionada;
    }
}

// Algunos navegadores cargan las voces de manera asíncrona, por lo que esperamos a que estén listas
if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = configurarVozFemenina;
}
// También lo ejecutamos de inmediato por si ya están cargadas (ej. Safari)
configurarVozFemenina();
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
        // Estilo Usuario: Burbuja gris claro a la derecha
        htmlContent = `
            <div class="bg-[#f0f4f9] text-gray-800 px-6 py-3.5 rounded-3xl max-w-[85%] md:max-w-[75%] text-[15px] leading-relaxed">
                ${texto}
            </div>
        `;
    } else {
        // Estilo Consultina: Avatar con destello a la izquierda, sin burbuja
        htmlContent = `
            <div class="flex gap-4 w-full md:max-w-[90%]">
                <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0 mt-1">
                    <span class="text-white text-[15px] font-bold">✦</span>
                </div>
                <div class="text-gray-800 text-[15px] leading-relaxed w-full">
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
    
    statusText.innerHTML = '<span class="text-primary font-medium">Te estoy escuchando...</span>';
    
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
    
    statusText.innerHTML = 'Consultina está analizando...';
    
    // Ícono de Micrófono
    iconMic.innerHTML = '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" x2="12" y1="19" y2="22"></line>';
};

reconocimiento.onerror = () => {
    statusText.innerText = 'Toca el micrófono y haz tu pregunta a Consultina...';
};

// 5. Enviar a Rasa y leer respuesta
reconocimiento.onresult = async (event) => {
    const textoUsuario = event.results[0][0].transcript;
    agregarMensaje("Tú", textoUsuario, true);

    try {
        const respuesta = await fetch("http://localhost:5005/webhooks/rest/webhook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sender: "usuario_demo", message: textoUsuario })
        });

        const data = await respuesta.json();
        
        if(data && data.length > 0) {
            let textoParaVoz = ""; 
            
            data.forEach(mensaje => {
                if(mensaje.text) {
                    let textoHTML = mensaje.text
                        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-primary font-semibold">$1</strong>')
                        .replace(/\n/g, '<br>');
                    
                    agregarMensaje("Consultina", textoHTML, false);
                    textoParaVoz += mensaje.text.replace(/\*/g, '') + ". ";
                }
            });
            
            voz.text = textoParaVoz;
            window.speechSynthesis.speak(voz);
        }
    } catch (error) {
        agregarMensaje("Sistema", "Error de conexión con el servidor de IA.", false);
    } finally {
        statusText.innerText = 'Toca el micrófono y haz tu pregunta a Consultina...';
    }
};