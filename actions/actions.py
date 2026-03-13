import mysql.connector
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