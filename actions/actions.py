import mysql.connector
import google.generativeai as genai
from mysql.connector import Error
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class ActionConsultarCuposCapacitadora(Action):
    def name(self) -> Text:
        return "action_consultar_cupos_capacitadora"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtenemos el curso de la memoria de la IA
        carrera_slot = tracker.get_slot("carrera")
        
        # Diccionario para presentar los nombres de forma profesional
        nombres_formateados = {
            "veterinaria": "Veterinaria",
            "enfermeria": "Enfermería",
            "rehabilitacion fisica": "Rehabilitación Física",
            "administracion de farmacias": "Farmacia",
            "educacion inicial": "Educación Inicial",
            "naturopatia": "Naturopatía",
            "emergencias medicas": "Emergencias Médicas",
            "odontologia": "Odontología",
            "laboratorio clinico": "Laboratorio Clínico",
            "flores de bach": "Flores de Bach",
            "mecanica de motos": "Mecánica básica de motos para mujeres",
            "mecanica automotriz": "Mecánica básica de vehículos",
            "inyectologia": "Taller de Inyectología"
        }

        # ESCENARIO 1: El usuario SÍ mencionó el curso
        if carrera_slot:
            carrera_normalizada = carrera_slot.lower().strip()
            nombre_bonito = nombres_formateados.get(carrera_normalizada, carrera_slot.title())
            cupos_disponibles = None
            conexion = None

            # Conexión a la Base de Datos
            try:
                conexion = mysql.connector.connect(
                    host='127.0.0.1',
                    database='istcge_admisiones',
                    user='asesor_ia',
                    password='admin123'
                )
                if conexion.is_connected():
                    cursor = conexion.cursor(dictionary=True, buffered=True)
                    
                    # Consulta a tu tabla cursos_capacitadora
                    query = "SELECT cupos FROM cursos_capacitadora WHERE nombre LIKE %s"
                    cursor.execute(query, (f"%{carrera_normalizada}%",))
                    resultado = cursor.fetchone()

                    if resultado:
                        cupos_disponibles = resultado["cupos"]

            except Error as e:
                print(f"Error conectando a MySQL (cursos): {e}")
            finally:
                if conexion is not None and conexion.is_connected():
                    cursor.close()
                    conexion.close()

            # Responder si encontró los cupos en la BDD
            if cupos_disponibles is not None:
                mensaje = f"¡Sí! Aún contamos con cupos disponibles para el curso de **{nombre_bonito}**.\n\nActualmente nos quedan **{cupos_disponibles} cupos disponibles**.\n\nSi te interesa, lo ideal es asegurar tu espacio lo antes posible. ¿Te gustaría que te ponga en contacto con mi asistente Daniela para reservar tu lugar?"
            else:
                mensaje = f"En este momento mi asistente Daniela puede confirmarte los cupos exactos para el curso de **{nombre_bonito}**.\n\n¡Le he notificado para que revise el sistema y te responda enseguida!"
            
            dispatcher.utter_message(text=mensaje)

        # ESCENARIO 2: El usuario NO mencionó el curso o el micrófono lo cortó ("hay cupos disponibles para...")
        else:
            mensaje = "¡Sí! Nuestros cursos manejan cupos limitados, ya que buscamos mantener grupos pequeños para que cada estudiante aprenda de manera práctica.\n\n**¿De qué curso en específico te gustaría saber si aún tenemos cupos disponibles?** (Ej: Flores de Bach, Veterinaria, Farmacia...)"
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

class ActionConsultarCupos(Action):
    def name(self) -> Text:
        return "action_consultar_cupos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Obtenemos la carrera de la memoria de la IA
        carrera_slot = tracker.get_slot("carrera")
        
        # Diccionario para presentar los nombres de forma profesional
        nombres_formateados = {
            "enfermeria": "Enfermería",
            "emergencias medicas": "Emergencias Médicas",
            "rehabilitacion fisica": "Rehabilitación Física",
            "laboratorio clinico": "Laboratorio Clínico",
            "administracion de farmacias": "Administración en Farmacias",
            "administracion de sistemas de la salud": "Administración de Sistemas de la Salud",
            "educacion inicial": "Educación Inicial",
            "administracion": "Administración",
            "marketing digital": "Marketing Digital y Comercio Electrónico",
            "desarrollo de contenidos y manejo de redes": "Desarrollo de Contenidos y Manejo de Redes",
            "mecanica automotriz": "Mecánica Automotriz",
            "gastronomia": "Gastronomía",
            "naturopatia": "Naturopatía",
            "inteligencia artificial": "Inteligencia Artificial"
        }

        # ESCENARIO 1: El usuario SÍ mencionó la carrera
        if carrera_slot:
            carrera_normalizada = carrera_slot.lower().strip()
            nombre_bonito = nombres_formateados.get(carrera_normalizada, carrera_slot.title())
            cupos_disponibles = None
            conexion = None

            # Conexión a la Base de Datos
            try:
                conexion = mysql.connector.connect(
                    host='127.0.0.1',
                    database='istcge_admisiones',
                    user='asesor_ia',
                    password='admin123'
                )
                if conexion.is_connected():
                    cursor = conexion.cursor(dictionary=True, buffered=True)
                    
                    # Consulta exacta a tu tabla 'carreras'
                    query = "SELECT cupos FROM carreras WHERE nombre LIKE %s"
                    cursor.execute(query, (f"%{carrera_normalizada}%",))
                    resultado = cursor.fetchone()

                    if resultado:
                        cupos_disponibles = resultado["cupos"]

            except Error as e:
                print(f"Error conectando a MySQL (carreras): {e}")
            finally:
                if conexion is not None and conexion.is_connected():
                    cursor.close()
                    conexion.close()

            # Responder si encontró los cupos en la BDD
            if cupos_disponibles is not None:
                mensaje = f"¡Sí! Aún contamos con cupos disponibles para la carrera de **{nombre_bonito}**.\n\nActualmente nos quedan **{cupos_disponibles} cupos disponibles**.\n\nTe recordamos que por procesos de calidad internacionales, solo recibimos hasta 25 personas por aula para garantizar tu aprendizaje.\n\n¿Te gustaría que te ponga en contacto con mi asistente Daniela para que te ayude a asegurar tu cupo antes de que se agoten?"
            else:
                # Si la carrera no está en la BDD
                mensaje = f"En este momento mi asistente Daniela puede confirmarte los cupos exactos disponibles para la carrera de **{nombre_bonito}**.\n\n¡Le he notificado para que revise el sistema y te responda enseguida!"
            
            dispatcher.utter_message(text=mensaje)

        # ESCENARIO 2: El usuario NO mencionó la carrera ("¿Tienen cupos?")
        else:
            mensaje = "¡Sí! Aún contamos con cupos disponibles para nuestras carreras de Tecnología Superior. Sin embargo, por procesos de calidad internacionales, solo recibimos hasta 25 personas por aula.\n\n**¿De qué carrera en específico te gustaría saber la disponibilidad para revisar el sistema?**"
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

# 3. Lista de tus API Keys (Rotador)
        # Reemplaza estos textos con tus 10 API keys reales
        api_keys = [
            "AIzaSyD3o3yp3gGeSb7WX4kXwgxDMJznGcwoTLw", # Tu llave actual
            "AIzaSyAgNW19aIMGfGGvHAHl-nNBkrokd0CKft4",
            "AIzaSyBecjaFKCcCFXmM6_dCI2BcHeaWKsMYQKE",
            "AIzaSyBZFJxLp3HalsLg8I7Ft9U9rv62MIe827Q",
            "AIzaSyD12dqpT6876mk93iHUHmweTz9usMR7dNE",
            "AIzaSyD9C6LoTAZ8LGtlIYe_U3t6Qmgnj33EtgE",
            "AIzaSyBoYvQnAfZ5nyoF44_lbxmFJ8v5O2XgT1c",
            "AIzaSyCL60avJYx2N5QakLFDXE19v7dfwUt5t9Y",
            "AIzaSyBqS_cHSSgZd03WhhUnsySCX1o9mG1FYq8",
            "AIzaSyD9C6LoTAZ8LGtlIYe_U3t6Qmgnj33EtgE",
            "AIzaSyBoYvQnAfZ5nyoF44_lbxmFJ8v5O2XgT1c",
            "AIzaSyCL60avJYx2N5QakLFDXE19v7dfwUt5t9Y",
            "AIzaSyBqS_cHSSgZd03WhhUnsySCX1o9mG1FYq8",
            "AIzaSyDhNSqZxzci-KY7QKo2JQs4orUGrrkoiZU",
            "AIzaSyB5jflp7MZxOByMkMkW8WYaBTyX09nWI7I",
            "AIzaSyARyXgXBSCvVipLQi2OhKsOfMiOaH0M50Y",
            "AIzaSyDuj8DDoT5pQFz_XZe7qjFwmx8Hr4o8a8k",
            "AIzaSyCu2AOvQKzxJXcbY0kFjJqIczXdf-n7MwU",
            "AIzaSyBIR9cCOYEg8VFlNgLvR94_1BGOPkXTi_c",
            "AIzaSyCalOgcaPA15bYXza_VJl-5Li4tIz-6U-0",
            "AIzaSyCtrClxyOU0t4B0QHIcEE-74871GycrtOA",
            "AIzaSyBclIP81appgVKWnO9tWn6OFWfdrJ2A7ag",
            "AIzaSyDweQIZYHrN0ZF2GD6xoDjSZeXbmLP3UVk",
            "AIzaSyARAJLbN4_vQplJfFqpxha6IzvDkRTsFe4",
            "AIzaSyC7S70LC5L3ithFV8kX5gcUYHrXv8IMF1U",
            "AIzaSyBgYcEo7pJyfFBdLfEJE9Hiz4m7C1NFUPo",
            "AIzaSyBeAztzQ9bhFDsB9tvks037Me1x_xWrD6A",
            "AIzaSyCpTXgsrmVhbpGGGX3BYB3tMvLNbHlUm3k",
            "AIzaSyDEv5pjOoCo4_A3dOs9g0MV0QuNXP4r-ao",
            "AIzaSyDbEUTHRhlNtf3HF3CkhStFiZno1lj5p0M",
            "AIzaSyCIXfoFbHFR6MgvM9U4qZd3aTdm6WRGkeU",
            "AIzaSyCyFVK1e5g5nj5Zuzl1W8zw9Ep0Z1iuV4s",
            "AIzaSyDedS6xOo7HyHUoMaZBAlTuoJ_lsj-iPZI",
            "AIzaSyDJn_I5PGbs1_vHohpnPEsFLfFcoTVkWco",
            "AIzaSyAhjtZ6ZyNlt8A989WgP4xhTSx5-8RYdkQ",
            "AIzaSyBt_n2n99QIdxmGK5ThqvTItliTdyhkvzA",
            "AIzaSyDWBBpcLAptPyG3olhEGR9sgkTV51DMMvE",
            "AIzaSyB0LqEm3iGO49CZucQEunAepSsO0S6Ah4Y",
            "AIzaSyC_Asvv9slgM4WjvHNFUgnBgm0XmJAThFc",
            "AIzaSyDwE3C-3NxazjSCVUBN9-UG3MBhe-DyWj0",
            "AIzaSyBtjbC8CrajDNsOSBw0zFMnBIYyYs5NC0I",
            "AIzaSyAiA4yBWYEhvN3nXxThoKPa1iPkuFF8-UM",
            "AIzaSyBYh7DWmTjFBu_z5OsaPh8A-q1LJ6C1ZhQ",
            "AIzaSyCz6EgEg8HwGeJJOVTeoazDb7dc7lB0nls",
            "AIzaSyBHHl0outkrOFJq_OYsxLCVFnNM8q30DyI",
            "AIzaSyBmdIWb8Bs238O-OXtf2L5UKydW82mKgWA",
            "AIzaSyD54NX250xRbQlGXJYfhPJrnAEZUq_8AJc",
            "AIzaSyBbDcywtnG7l9Yu_N8snHjpYTVDrMuueKM",
            "AIzaSyCG4dqr2WONXw5cKT-HF71GpjyFoDcGNkI",
            "AIzaSyBVz27bpk0kACgBH5AattldIuDmmzTJHno",
            "AIzaSyD0BlJ6g_UgMwHxbiaSyTSN6fy9YnUumH0",
            "AIzaSyCHumRMKRfTL_b44_aEPYJht44PfyH_ZfA",
            "AIzaSyCFrAE36-6Q1xTCpala1QCUaQWo3leLTC4",
            "AIzaSyBzPMKTYYl2xRfVGWPrM8aoELy3WhL3qB0",
            "AIzaSyDN3341-VFEe2L3EhOV8FzbCDMoqiHMkug",
            "AIzaSyADqQO2hRnZufzhnubK_O9SUsdzzuWXhSI",
            "AIzaSyA4i2bdp6gjBFGAVqV7ahAvyBqbHDD8viA",
            "AIzaSyArDCSiYDdvuvsYv9nk52w4ffHuGE88yQU"
        ]

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

        # 5. Bucle del Rotador de APIs
        respuesta_exitosa = False

        for api_key in api_keys:
            try:
                # Configuramos la API con la llave actual del bucle
                genai.configure(api_key=api_key)
                
                model = genai.GenerativeModel(
                    'gemini-2.5-flash',
                    system_instruction=instrucciones_sistema,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                
                # Intentamos generar la respuesta
                respuesta_gemini = model.generate_content(prompt_completo)
                dispatcher.utter_message(text=respuesta_gemini.text)
                
                # Si llega hasta aquí sin dar error, significa que funcionó. 
                # Rompemos el bucle para no seguir gastando las otras APIs.
                respuesta_exitosa = True
                break 

            except Exception as e:
                # Si falla (por cuota excedida, por ejemplo), imprimimos el error en consola 
                # y el bucle continuará automáticamente con la siguiente API Key.
                print(f"⚠️ API Key terminada en ...{api_key[-4:]} falló. Intentando con la siguiente... Error: {e}")
                continue

        # 6. Fallback final de emergencia
        # Si TODAS las APIs de la lista fallaron (se agotaron todas las cuotas)
        if not respuesta_exitosa:
            print("TODAS LAS API KEYS SE HAN AGOTADO.")
            dispatcher.utter_message(
                text="Esa es una excelente pregunta que mi asistente Daniela te podría responder de manera más precisa y detallada.\n\nLe he notificado para que te responda enseguida."
            )

        return []
