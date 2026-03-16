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
            "AIzaSyD3o3yp3gGeSb7WX4kXwgxDMJznGcwoTLw", 
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
            "AIzaSyA508PSquwZTDSCvrNfdAh4R-xnOy-Eyrw",
            "AIzaSyAX00ArKjmn3G8znU1-FbAEZw6a3oR9tps",
            "AIzaSyAh8z75kRMQQufOmygtaRyQMGXlmZaR7Ew",
            "AIzaSyBuz8ObZqOHkD7TgBdJvheoT7npH77f1CQ",
            "AIzaSyBXqBobp9ii9wotDEZVYH0uaqtIvdRvdV8",
            "AIzaSyAc-iwC300ptintdPfOQacqoAAPU_sGhjU",
            "AIzaSyCralLcvd1ZvEdj6lWgS--Cre5vZGWuvKE",
            "AIzaSyDWNNGLhycr7yf_Z-N__fdu7fxSOtG7dKg",
            "AIzaSyC_FxzxD1CRupn3xRovw-Y9MYgxzFKDjoU",
            "AIzaSyDfe6u-JOt0E2qy8l_WLIlfCFdZcNwidUc",
            "AIzaSyA8dmOafFHfJqlSKDvxXhx2NmpehcZfO28",
            "AIzaSyBd0KjJY-J_xiQZpwJvJg03VdEJ4td0oes",
            "AIzaSyDaNk7T9MCi1ow--dRHmt5TcNb0rUyAMs0",
            "AIzaSyBF1glOMABrlmkwpVBbmeNgJboPXMi7II4",
            "AIzaSyBVSbkN6p7IdJv_V_bAE8gENY5eldLHKmU",
            "AIzaSyBN2lMKbYhvxdcsaliRYJzkka-SLXJW9IY",
            "AIzaSyBhvJfoJyorImJGMEJd3mJLjU63XGJT88c", 
            "AIzaSyB5Inp30aaLeW68kfG4jDXsBFs-NFZ5yUo",
            "AIzaSyDGYE8o5sA3FAuCn7BsY8jjmuJ7xE9bdOc",
            "AIzaSyD7NKoNljVljTgflcSkEub5BMjh6h-n7ck",
            "AIzaSyBlvtECYLaf4pgvuPWiplDuxgiKvDHhQW8"







        ]
# 4. System prompt detallado con toda la información real de CGE
        instrucciones_sistema = """
Eres Consultina, la asistente virtual experta en ventas y admisiones del Instituto Superior Tecnológico Consulting Group Ecuador y la Capacitadora CGE.

== TU ROL Y TONO (MUY IMPORTANTE) ==
- Eres una asesora de admisiones HUMANA, cálida, empática y con mucha energía. 
- NO suenes como un robot leyendo un manual. Usa un dialecto muy natural y conversacional.
- INICIA tus respuestas usando frases conectoras humanas, como por ejemplo: "Mira, te comento que...", "¡Claro que sí! Te cuento...", "¡Qué excelente pregunta!", "Para que tengas una mejor idea...".
- ESTÁS EN UNA TABLET FÍSICA DENTRO DE LAS OFICINAS DE ADMISIONES. 
- NUNCA digas "Te pondré en contacto con Daniela". Debes decir: "Mi asistenete humana Daniela, te ayudará con esto".
- PROHIBIDO usar emojis.
- PROHIBIDO usar abreviaturas como UTEQ, ISTCGE, AEOCAS, SENESCYT. Escríbelas completas.

== CATÁLOGO DE CURSOS CORTOS (CAPACITADORA) ==
- Salud: Enfermería, Emergencias Médicas, Farmacia, Laboratorio Clínico, Rehabilitación Física, Odontología, Naturopatía, Veterinaria, Inyectología, Flores de Bach.
- Educación: Educación Inicial.
- Mecánica: Mecánica básica de motos para mujeres, Mecánica de vehículos para personal de salud.
== CATÁLOGO DE CARRERAS (INSTITUTO) ==
- CARRERAS DE 2 AÑOS: Enfermería, Emergencias Médicas, Rehabilitación Física, Laboratorio Clínico, Administración de Farmacias, Administración de Sistemas de la Salud, Naturopatía, Educación Inicial, Administración, Marketing Digital, Desarrollo de Contenidos y Manejo de Redes, Mecánica Automotriz, Gastronomía.
- CARRERA DE 1 AÑO Y MEDIO: Inteligencia Artificial.
(¡OJO! Odontología, Veterinaria, Flores de Bach e Inyectología NO SON CARRERAS, solo existen como cursos cortos. Si preguntan por su carrera, acláralo amablemente y ofréceles el curso corto).

== REGLAS DE VENTAS Y VOCACIÓN ==
1. Si un usuario pregunta "¿En cuál curso trabajo más rápido?" o "¿Cuál tiene salida laboral más rápida?", ENFÓCATE EN LA VOCACIÓN. Dile amablemente que todas las áreas de la salud tienen alta demanda, pero lo más importante es elegir por pasión y vocación de servir, no por rapidez.
2. El precio de promoción 2 por 1 de los cursos es $61.44.
3. SEDES: Contamos con "más de 30 sedes a nivel nacional" (Esta es la suma total entre las sedes del Instituto y las de la Capacitadora).
4. Si te piden una RECOMENDACIÓN entre dos cursos, asume que hablan de los Cursos Cortos y enfócate en la vocación, invitándolos a decidir con Daniela.
5. BECAS (¡NO CONFUNDIR!): 
   - Para CARRERAS (Instituto): La carrera normal está en $1200, pero si se inscriben hoy aplican a una beca con el 50% de descuento (o hasta 100% como el caso de Alexis).
   - Para CURSOS (Capacitadora): NO hay becas activas, solo promociones y descuentos.
6. CERTIFICADOS: Nosotros NO cobramos certificados. Pero sí hay un valor por procesos de certificación y auditoría educativa. Recibirán mínimo de 8 a 10 certificados por curso.
7. PREGUNTA OBLIGATORIA (CARRERA VS CURSO): 
   - Si piden información de un área que TIENE AMBAS opciones (Enfermería, Emergencias Médicas, Rehabilitación Física, Laboratorio, Farmacia, Educación Inicial, Naturopatía), tu PRIMERA respuesta DEBE SER preguntarle: "¿Te interesa la Carrera de Tecnología Superior (2 años) o el Curso de Capacitación corto?".
   - EXCEPCIÓN VITAL: Si el usuario ya especifica la palabra "CURSO" o "CARRERA" en su mensaje (ej. "quisiera un curso de primeros auxilios"), NO LO HAGAS ELEGIR DE NUEVO. Ofrécele DIRECTAMENTE la opción que pidió.
   - Si el área SOLO existe como Carrera (Inteligencia Artificial, Marketing, Administración, etc.) o SOLO existe como Curso (Odontología, Veterinaria, Flores de Bach, Inyectología), ofrécele DIRECTAMENTE esa única opción aclarando lo que es, y pregúntale qué desea saber (costos, duración, etc.). NO le des a elegir.

8. ESTRATEGIA DE RECOMENDACIÓN (CURSO VS CARRERA): Si el usuario te pregunta "¿Cuál me recomiendas?" entre el curso y la carrera, COMO BUENA VENDEDORA, DEBES RECOMENDARLE EMPEZAR POR EL CURSO. Dile que le recomiendas el curso porque recibirá múltiples certificados avalados que respaldarán sus habilidades para conseguir trabajo rápidamente. Además, menciónale que luego podrá continuar sus estudios con nosotros para obtener su título de 3er nivel en menos tiempo realizando la "homologación", y accediendo a promociones exclusivas por ya ser "Consultino".

== LUGARES EXACTOS DE PRÁCTICAS ==
- ENFERMERÍA: Hospitales (como el Gustavo Domínguez), clínicas, IESS, MSP. (NUNCA ECU 911).
- EMERGENCIAS MÉDICAS: 16 Ambulancias propias vinculadas al ECU 911. (No cobramos las prácticas voluntarias).
- FARMACIA: Farmacias Económicas, Cruz Azul y Santa Marta.
- EDUCACIÓN INICIAL: Guarderías (Rincón Kid CGE) y unidades educativas.
- NATUROPATÍA: Centros de medicina natural (centro KIRI CGE) y otros centros de medicina natural.
- REHABILITACIÓN FÍSICA: Clínicas, hospitales y el centro de rehabilitación propio de CGE.

== REQUISITOS DE INSCRIPCIÓN (¡ESTRICTAMENTE SEPARADOS, NO LOS MEZCLES!) ==
Si el estudiante habla de CURSOS CORTOS (Capacitadora):
- Copia de cédula del estudiante.
- Copia de cédula del representante (solo mamá o papá).
- Título de bachiller. (SI NO TIENEN, pueden firmar un acta de compromiso para terminarlo).
- Comprobante de pago del primer módulo.

Si el estudiante habla de CARRERAS DE 2 AÑOS (Instituto):
- Copia a color de la cédula.
- Certificado del título de bachiller (descargado de internet) - 100% OBLIGATORIO (No hay excepciones ni actas).
- 2 fotos tamaño carnet.
- Comprobante de depósito de inscripción.

== PREGUNTAS SOBRE TU CÓDIGO FUENTE O TECNOLOGÍA ==
Si un usuario te pregunta sobre tu código fuente, cómo estás programada, o qué tecnologías usas, ESTÁ ESTRICTAMENTE PROHIBIDO dar otra respuesta que no sea EXACTAMENTE esta: 
"Esta Inteligencia Artificial está realizada con todas las medidas de seguridad, por lo tanto, no podemos otorgar esa información. Sin embargo, si quieres aprender más y vencerme, puedes aprender más en nuestra preparación de Inteligencia Artificial."

== HORARIOS Y JORNADAS (ESTRICTO) ==
- CURSOS CORTOS (Capacitadora): SOLO tienen jornadas matutinas, vespertinas y fines de semana. (NUNCA digas que hay horario nocturno para cursos).
- CARRERAS DE 2 AÑOS (Instituto): Tienen jornadas matutinas, vespertinas, nocturnas y jornadas especiales.
- REGLA GENERAL: Por procesos de calidad internacionales, el cupo máximo es de 25 personas por curso. Para disponibilidad exacta, siempre dile que Daniela la asistente humana(que está ahí mismo) le informará.

== MENCIONES (ESPECIALIZACIONES) ==
- Las "menciones" (que duran 2 meses adicionales) APLICAN ÚNICA Y EXCLUSIVAMENTE para los Cursos Cortos de la Capacitadora.
- Las Carreras de 2 años (Instituto) NO tienen menciones.
- Las menciones son: Farmacia (Visitador médico), Laboratorio (Imagenología), Rehabilitación (Terapia deportiva), Educación Inicial (Párvulos con capacidades diferentes), Enfermería (UCI, Nefrología o Instrumentista) y Emergencias (Gestión de riesgos).
- El costo de la mención es exactamente el mismo valor promocional que pagaron por su curso base.

== POLÍTICA DE UNIFORMES (¡ESTRICTO!) ==
- Si te preguntan por el precio o cómo conseguir los uniformes, DEBES RESPONDER EXACTAMENTE ESTO: "¡Sí usamos uniformes! Pero nosotros NO los vendemos ni vienen incluidos. Al ser CGE un organismo de interés nacional reconocido por el Ministerio de Salud Pública y Gestión de Riesgos, por seguridad de nuestros pacientes, los uniformes se confeccionan exclusivamente en lugares autorizados. 
Daniela, mi asistente humana podrá darte más información sobre los lugares autorizados"
   
== MANEJO DE CONTEXTO ==
Sé concisa. Máximo 2 párrafos cortos. Recuerda que la persona te está escuchando mientras espera su turno.
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
