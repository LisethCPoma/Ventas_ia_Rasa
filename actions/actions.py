import mysql.connector
import google.generativeai as genai
from mysql.connector import Error
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionConsultarCuposCapacitadora(Action):
    def name(self) -> Text:
        return "action_consultar_cupos_capacitadora"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtenemos la carrera/curso de la memoria de la IA
        carrera_slot = tracker.get_slot("carrera")
        
        # Simulador de Base de Datos de Cupos (Asegúrate de que coincida con tus datos)
        cupos_db = {
            "educacion inicial": 2,
            "emergencias medicas": 3,
            "enfermeria": 4,
            "administracion de farmacias": 5,
            "flores de bach": 2,
            "laboratorio clinico": 3,
            "mecanica de motos": 3,
            "mecanica automotriz": 4,
            "naturopatia": 2,
            "odontologia": 3,
            "rehabilitacion fisica": 3,
            "inyectologia": 2,
            "veterinaria": 2,
            "inteligencia artificial": 5,
            "gastronomia": 4
        }

        # Nombres formateados para que se vean profesionales en el chat
        nombres_bonitos = {
            "educacion inicial": "Educación Inicial",
            "emergencias medicas": "Emergencias Médicas",
            "enfermeria": "Enfermería",
            "administracion de farmacias": "Farmacia",
            "flores de bach": "Flores de Bach",
            "laboratorio clinico": "Laboratorio Clínico",
            "mecanica de motos": "Mecánica básica de motos para mujeres",
            "mecanica automotriz": "Mecánica básica de vehículos",
            "naturopatia": "Naturopatía",
            "odontologia": "Odontología",
            "rehabilitacion fisica": "Rehabilitación Física",
            "inyectologia": "Taller de Inyectología",
            "veterinaria": "Veterinaria",
            "inteligencia artificial": "Inteligencia Artificial",
            "gastronomia": "Gastronomía"
        }

        # ESCENARIO 1: El usuario SÍ mencionó el curso o ya venían hablando de él
        if carrera_slot and carrera_slot.lower() in cupos_db:
            cupos = cupos_db[carrera_slot.lower()]
            nombre_curso = nombres_bonitos.get(carrera_slot.lower(), carrera_slot.title())
            
            mensaje = f"¡Sí! Nuestros cursos manejan cupos limitados para garantizar una enseñanza 100% práctica.\n\nPara el curso de **{nombre_curso}**, actualmente nos quedan **{cupos} cupos disponibles**.\n\nSi te interesa, lo ideal es asegurar tu espacio lo antes posible. ¿Te gustaría que te ponga en contacto con mi asistente Daniela para reservar tu lugar?"
            dispatcher.utter_message(text=mensaje)
            
        # ESCENARIO 2: El usuario NO mencionó el curso ("¿Tienen cupos?")
        else:
            mensaje = "¡Sí! Nuestros cursos manejan cupos limitados, ya que buscamos mantener grupos pequeños de máximo 25 personas para que cada estudiante aprenda de manera práctica.\n\n**¿De qué curso en específico te gustaría saber si aún tenemos cupos disponibles?** (Ej: Flores de Bach, Veterinaria, Farmacia...)"
            dispatcher.utter_message(text=mensaje)

        return []


class ActionConsultarCuposCapacitadora(Action):
    """Consulta la tabla cursos_capacitadora y lista todos los cupos disponibles en tiempo real."""

    def name(self) -> Text:
        return "action_consultar_cupos_capacitadora"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Diccionario para presentar nombres con tildes correctas
        nombres_formateados = {
            "veterinaria": "Veterinaria",
            "enfermeria": "Enfermería",
            "rehabilitacion fisica": "Rehabilitación Física",
            "farmacia": "Farmacia",
            "educacion inicial": "Educación Inicial",
            "naturopatia": "Naturopatía",
            "emergencias medicas": "Emergencias Médicas",
            "odontologia": "Odontología",
            "laboratorio clinico": "Laboratorio Clínico",
            "flores de bach": "Flores de Bach",
            "mecanica motos mujeres": "Mecánica básica de motos para mujeres",
            "mecanica vehiculos salud": "Mecánica básica de vehículos (Personal de salud)",
            "taller inyectologia": "Taller de Inyectología",
        }

        conexion = None
        try:
            conexion = mysql.connector.connect(
                host='127.0.0.1',
                database='istcge_admisiones',
                user='asesor_ia',
                password='admin123'
            )
            if conexion.is_connected():
                cursor = conexion.cursor(dictionary=True, buffered=True)
                cursor.execute("SELECT nombre, cupos FROM cursos_capacitadora ORDER BY nombre")
                filas = cursor.fetchall()

                if filas:
                    lineas = []
                    for fila in filas:
                        nombre_bd = fila["nombre"].lower().strip()
                        nombre_bonito = nombres_formateados.get(nombre_bd, fila["nombre"].title())
                        lineas.append(f"- {nombre_bonito}: **{fila['cupos']} cupos disponibles**")

                    lista_cupos = "\n".join(lineas)
                    mensaje = (
                        "¡Sí! Nuestros cursos manejan cupos limitados, ya que buscamos mantener grupos adecuados "
                        "para que cada estudiante pueda aprender de manera práctica y con el acompañamiento necesario.\n\n"
                        f"Actualmente la disponibilidad de cupos es la siguiente:\n{lista_cupos}\n\n"
                        "Si alguno de estos cursos te interesa, lo ideal es asegurar tu cupo lo antes posible, ya que "
                        "cuando se completan los espacios disponibles debemos esperar a la apertura del siguiente grupo.\n\n"
                        "¿Te gustaría iniciar el proceso de inscripción o que ponga en contacto con mi asistente Daniela para reservar tu cupo?"
                    )
                else:
                    mensaje = (
                        "En este momento mi asistente Daniela puede confirmarte los cupos exactos disponibles para cada curso. "
                        "¡Le he notificado para que te responda enseguida!"
                    )
        except Error as e:
            print(f"Error conectando a MySQL (cursos_capacitadora): {e}")
            mensaje = (
                "Esa es una excelente pregunta que mi asistente Daniela te podría responder de manera mucho más precisa.\n\n"
                "Le he notificado tu consulta para que revise el sistema y confirme directamente los cupos contigo enseguida."
            )
        finally:
            if conexion is not None and conexion.is_connected():
                cursor.close()
                conexion.close()

        dispatcher.utter_message(text=mensaje)
        return []

class ActionGeminiFallback(Action):
    def name(self) -> Text:
        return "action_gemini_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 1. Obtener el último mensaje del usuario
        mensaje_usuario = tracker.latest_message.get('text', '')

        # 2. Recuperar el historial reciente de conversación (últimos 6 turnos)
        historial = []
        for evento in tracker.events[-20:]:
            if evento.get('event') == 'user':
                historial.append(f"Usuario: {evento.get('text', '')}")
            elif evento.get('event') == 'bot':
                texto_bot = evento.get('text') or ''
                if texto_bot:
                    historial.append(f"Consultina: {texto_bot[:200]}")  # recortamos respuestas largas

        contexto_historial = "\n".join(historial[-12:])  # últimos ~6 intercambios

        # 3. Configurar la API de Gemini
        genai.configure(api_key="AIzaSyD3o3yp3gGeSb7WX4kXwgxDMJznGcwoTLw")

        # 4. System prompt detallado con toda la información real de CGE
        instrucciones_sistema = """
Eres Consultina, la asistente virtual experta en ventas y admisiones del Instituto Superior Tecnológico Consulting Group Ecuador (ISTCGE) y su Capacitadora CGE.

== IDENTIDAD ==
- Tu nombre es Consultina.
- Eres amable, persuasiva y hablas en español de forma muy natural y cercana.
- PROHIBIDO usar emojis (el sistema de voz los lee literalmente y arruina la experiencia).
- Sé breve: máximo 2 párrafos cortos, a menos que el usuario pida una lista detallada.

== SOBRE EL INSTITUTO (ISTCGE) ==
Carreras de 2 años (Tecnología Superior - título SENESCYT):
- ÁREA SALUD: Enfermería, Emergencias Médicas, Rehabilitación Física, Laboratorio Clínico, Administración de Farmacias, Administración de Sistemas de la Salud.
- ÁREA EDUCATIVA: Educación Inicial.
- ÁREA EMPRESARIAL: Administración, Marketing Digital y Comercio Electrónico, Desarrollo de Contenidos y Manejo de Redes.
- ÁREA TÉCNICA: Mecánica Automotriz, Gastronomía.
- ÁREA BIENESTAR: Naturopatía.
- ÁREA TECNOLÓGICA: Inteligencia Artificial (1.5 años).
El instituto tiene 32 sedes a nivel nacional y más de dos décadas de trayectoria.

== SOBRE LA CAPACITADORA CGE ==
Cursos cortos 100% prácticos, organizados en módulos de 1 mes:
- Auxiliar de Enfermería (8 módulos), Emergencias Médicas (8 módulos), Rehabilitación Física (6 módulos), Laboratorio Clínico (5 módulos), Auxiliar de Farmacia (5 módulos), Odontología (5 módulos), Naturopatía (8 módulos), Veterinaria (8 módulos), Educación Inicial (8 módulos), Flores de Bach (4 módulos), Mecánica de motos para mujeres (2 módulos), Mecánica de vehículos para personal de salud (4 módulos), Taller de Inyectología (1 módulo).
Al finalizar, el estudiante recibe entre 8 y 10 certificados (UTQ, ISTCGE, AEOCAS, etc.).

== REGLAS DE VENTAS ==
1. NUNCA inventes precios exactos. Para costos y pagos, dile al usuario que MI ASISTENTE DANIELA le dará los valores exactos y las posibles promociones vigentes.
2. Si hablas de dinero, menciona: "Recuerda que todos los valores que dejes en CGE nos ayudan a salvar vidas."
3. Para homologación interna (Consultinos), el valor es $89.60 e incluye el cuadernillo, plataforma y usuario.
4. NUNCA respondas temas ajenos a educación, el instituto o sus cursos.
5. Siempre intenta cerrar con una pregunta que lleve al usuario al siguiente paso (hablar con Daniela, preguntar costos, iniciar inscripción).

== MANEJO DE CONTEXTO ==
Si el historial muestra que el usuario ya eligió una carrera o curso, responde en el contexto de esa elección. Nunca repitas información que ya diste.
"""

        prompt_completo = f"""Historial reciente de conversación:
{contexto_historial}

Pregunta actual del usuario: {mensaje_usuario}

Responde como Consultina siguiendo estrictamente las instrucciones del sistema."""

        try:
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                system_instruction=instrucciones_sistema
            )
            respuesta_gemini = model.generate_content(prompt_completo)
            dispatcher.utter_message(text=respuesta_gemini.text)

        except Exception as e:
            print(f"Error con Gemini API: {e}")
            dispatcher.utter_message(
                text="Esa es una excelente pregunta que mi asistente Daniela te podría responder de manera más precisa y detallada.\n\nLe he notificado para que te responda enseguida."
            )

        return []
