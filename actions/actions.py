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
                host='localhost', # o la IP de tu servidor MySQL
                database='istcge_admisiones', # Nombre de tu base de datos
                user='asesor_ia', # Tu usuario
                password='admin123' # Tu contraseña
            )

            if conexion.is_connected():
                # dictionary=True hace que el resultado vuelva como un array asociativo
                cursor = conexion.cursor(dictionary=True) 
                
                # 2. Ejecutar la consulta preparada (segura)
                query = "SELECT cupos FROM carreras WHERE nombre = %s"
                cursor.execute(query, (carrera_consultada,))
                
                # 3. Obtener el primer registro
                registro = cursor.fetchone()
                
                if registro:
                    cupos_disponibles = registro['cupos']
                    mensaje = f"¡Excelente! Revisando nuestra base de datos en vivo, para {carrera_consultada} nos quedan {cupos_disponibles} cupos."
                else:
                    mensaje = f"He buscado {carrera_consultada} en el sistema, pero no encontré registros de cupos en este momento."

        except Error as e:
            # Si se cae la base de datos, el bot no explota, simplemente avisa
            print(f"Error conectando a MySQL: {e}")
            mensaje = "Lo siento, en este momento nuestro sistema de admisiones está en mantenimiento. ¿Te puedo ayudar con algo más?"

        finally:
            # 4. Cerrar la conexión siempre para no saturar el servidor
            if conexion is not None and conexion.is_connected():
                cursor.close()
                conexion.close()

        # 5. Enviar la respuesta final al usuario en el chat
        dispatcher.utter_message(text=mensaje)

        return []