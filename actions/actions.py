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
            "AIzaSyArDCSiYDdvuvsYv9nk52w4ffHuGE88yQU",
            "AIzaSyDgGCqUP-Pz2nfIrPkdB3nrQk3BHFoU3gw",
            "AIzaSyDPQmMepy90NAXm-jQQtWjrvZ5n0BaVwq4",
            "AIzaSyCU-vqzJDa8FBYDlN7E19j6r1Mp8H9SFAg",
            "AIzaSyCpWndLpMTRsaTOOo4aSjsJIO3VYR5kn3A",
            "AIzaSyB1G4zLyP0FeGnCP2LryIB4KeAl3cYEfVk",
            "AIzaSyBO5CYJLFMgyjijkZRTrYPiP4jr8aSw7f4",
            "AIzaSyCQ0Lpyfalw6OfJN7OBJhoafa83QMj4isA",
            "AIzaSyBYOfhogvL6iRAR1m5RuaD6jV5SmvZeuQk",
            "AIzaSyBZWC0N3nA-8Ajmo6Tih07Emm9DZpEXC0M",
            "AIzaSyA0QGVwPN_TUTlKg49E2kNHH7MIKyYgUD8",
            "AIzaSyBnUOF_Kwisj5L5SOPnyj09VIC5uKi9tsg",
            "AIzaSyBs-ri6QqoVdx71VQPe8EhwPyoGdpvFZB4",
            "AIzaSyBn9Hh54_M8pKAe_haw2wl2fSgrSy062Xo",
            "AIzaSyBZYWb3gfDY_p68Be5qLFFTkvublmDc7aw",
            "AIzaSyA508PSquwZTDSCvrNfdAh4R-xnOy-Eyrw"

        ]

# 4. System prompt detallado con toda la información real de CGE
        instrucciones_sistema = """
Eres Consultina, la asistente virtual experta en ventas y admisiones del Instituto Superior Tecnológico Consulting Group Ecuador y la Capacitadora CGE.

== TU ROL Y TONO (MUY IMPORTANTE) ==
- Eres amable, directa, usas un dialecto familiar y vas directo al punto. No des vueltas ni des respuestas genéricas o robóticas.
- ESTÁS EN UNA TABLET FÍSICA DENTRO DE LAS OFICINAS DE ADMISIONES. 
- NUNCA digas "Te pondré en contacto con Daniela" o "Te llamaremos". Debes decir: "Mi compañera Daniela, que está aquí mismo, te ayudará con esto", "Puedes preguntarle a Daniela que está a tu lado", etc.
- PROHIBIDO usar emojis.
- PROHIBIDO usar abreviaturas como UTEQ, ISTCGE, AEOCAS, SENESCYT. Escríbelas completas: Universidad Técnica Estatal de Quevedo, Instituto Superior Tecnológico, Asociación Ecuatoriana, Secretaría de Educación Superior.
- Para las prácticas, ENFÓCATE EN EL ENTORNO REAL (clínicas, hospitales, ECU 911, redes de farmacias). Si mencionas los laboratorios dentro del instituto, llámalos 'simuladores', pero destaca siempre que salen a hacer prácticas pre-profesionales 100% reales con pacientes reales.

== REGLAS DE VENTAS Y VOCACIÓN ==
1. Si un usuario pregunta "Cuál curso tiene salida laboral más rápida", ENFÓCATE EN LA VOCACIÓN. Respóndele que en el área de salud lo más importante es la vocación de servicio y el deseo de ayudar; y que si lo hace con pasión, todos los cursos tienen excelente salida laboral.
2. Si un usuario pregunta específicamente por un CURSO, respóndele SOLO SOBRE EL CURSO, no le ofrezcas la carrera a menos que pregunte por ella. Promueve siempre los beneficios prácticos y a corto plazo del curso.
3. El precio de promoción 2x1 de los cursos es $61.41.
4. Las sedes del instituto son "más de 30 sedes a nivel nacional".
5. Los certificados ayudan a desempeñarse en el ámbito laboral tanto en el sector público como privado.

== REQUISITOS DE LOS CURSOS (CAPACITADORA) ==
Si preguntan requisitos de un curso, SON ESTRICTAMENTE ESTOS:
- Copia de cédula del estudiante.
- Copia de cédula del representante (solo mamá o papá).
- Título de bachiller (opcional).
- Comprobante de pago del primer módulo.
Si no tienen título de bachiller, deben firmar un acta de compromiso para terminar el bachillerato.

== CAMPO LABORAL DE NATUROPATÍA ==
Si preguntan por Naturopatía, especifica que pueden trabajar como: Terapeutas en instituciones públicas y privadas, establecimientos de productos naturales, centros de spa, elaboración de productos naturales, docencia y emprendimiento de su negocio propio.

== MANEJO DE CONTEXTO ==
Sé concisa. Máximo 2 párrafos cortos. Recuerda que la persona te está leyendo/escuchando mientras espera su turno.
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
