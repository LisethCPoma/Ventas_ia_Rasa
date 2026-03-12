import mysql.connector
from mysql.connector import Error
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionConsultarCupos(Action):
    def name(self) -> Text:
        return "action_consultar_cupos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        
        # Capturamos dinámicamente lo que el usuario pidió
        carrera_consultada = tracker.get_slot("carrera")

        if not carrera_consultada:
            dispatcher.utter_message(text="Para revisar los cupos, ¿podrías decirme qué carrera te interesa (Inteligencia Artificial, Marketing Digital o Administración)?")
            return []
            
        conexion = None

        try:
            # 1. Configurar la conexión a MySQL
            conexion = mysql.connector.connect(
                host='127.0.0.1', # Forzamos la red TCP para Docker
                database='istcge_admisiones',
                user='asesor_ia',
                password='admin123'
            )
            if conexion.is_connected():
                # dictionary=True hace que el resultado vuelva como un array asociativo
                # buffered=True soluciona el error "Unread result found"
                cursor = conexion.cursor(dictionary=True, buffered=True) 
                
                # 2. Ejecutar la consulta preparada (segura) usando LOWER para ignorar mayúsculas
                # Usamos LIKE con comodines '%' a ambos lados para coincidencias parciales (ej. 'Inicial' buscará '%Inicial%')
                query = "SELECT cupos, imagen_url FROM carreras WHERE LOWER(nombre) LIKE LOWER(%s)"
                carrera_comodin = f"%{carrera_consultada}%"
                cursor.execute(query, (carrera_comodin,))
                
                # 3. Obtener el primer registro
                registro = cursor.fetchone()
                
                if registro:
                    cupos_disponibles = registro['cupos']
                    imagen_url = registro.get('imagen_url')
                    
                    # Diccionario para corregir ortografía y mejorar la pronunciación TTS de la IA
                    nombres_formateados = {
                        "enfermeria": "Enfermería",
                        "emergencias medicas": "Emergencias Médicas",
                        "rehabilitacion fisica": "Rehabilitación Física",
                        "laboratorio clinico": "Laboratorio Clínico",
                        "administracion de farmacias": "Administración de Farmacias",
                        "administracion de sistemas de la salud": "Administración de Sistemas de la Salud",
                        "educacion inicial": "Educación Inicial",
                        "administracion": "Administración",
                        "marketing digital": "Marketing Digital",
                        "desarrollo de contenidos y manejo de redes": "Desarrollo de Contenidos y Manejo de Redes",
                        "mecanica automotriz": "Mecánica Automotriz",
                        "gastronomia": "Gastronomía",
                        "naturopatia": "Naturopatía",
                        "inteligencia artificial": "Inteligencia Artificial"
                    }
                    
                    # Obtenemos el nombre formateado. Si por algún motivo no está en el diccionario, usamos title()
                    nombre_presentacion = nombres_formateados.get(carrera_consultada.lower(), carrera_consultada.title())

                    mensaje = f"¡Excelente! Revisando nuestra base de datos en vivo, para {nombre_presentacion} nos quedan {cupos_disponibles} cupos."
                    
                    if imagen_url:
                        dispatcher.utter_message(text=mensaje, image=imagen_url)
                        return []
                    else:
                        dispatcher.utter_message(text=mensaje)
                        return []
                else:
                    nombre_presentacion = carrera_consultada.title()
                    # Mismo trato para el mensaje de error "no encontré registros"
                    if carrera_consultada.lower() == "enfermeria": nombre_presentacion = "Enfermería"
                    if carrera_consultada.lower() == "mecanica automotriz": nombre_presentacion = "Mecánica Automotriz"
                    if carrera_consultada.lower() == "naturopatia": nombre_presentacion = "Naturopatía"
                    # etc.
                    
                    mensaje = f"He buscado {nombre_presentacion} en el sistema, pero no encontré registros de cupos en este momento."

        except Error as e:
            # Si se cae la base de datos, el bot no explota, simplemente avisa
            print(f"Error conectando a MySQL: {e}")
            mensaje = "Esa es una excelente pregunta que Daniela te podría responder de manera mucho más precisa y detallada.\n\nLe he notificado tu consulta para que revise el sistema y pueda confirmar directamente los cupos contigo enseguida."

        finally:
            # 4. Cerrar la conexión siempre para no saturar el servidor
            if conexion is not None and conexion.is_connected():
                cursor.close()
                conexion.close()

        # 5. Enviar la respuesta final si no se despachó antes (ej. cuando no hay registros o hay error)
        try:
            dispatcher.utter_message(text=mensaje)
        except UnboundLocalError:
            pass

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