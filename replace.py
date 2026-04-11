import re

file_path = "domain.yml"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    "Enfermería": "¡Excelente elección! 💙 En Enfermería aprenderás a atender pacientes, apoyar en procedimientos médicos y gestionar tareas administrativas en salud.\\nSin embargo, yo te recomiendo comenzar con el curso de 8 meses, ya que es una opción económica que te brinda de 8 a 10 certificados, fortaleciendo tu hoja de vida. Este curso práctico es el primer paso hacia tu crecimiento profesional. Al terminar, puedes obtener tu Título de Tercer Nivel en solo un año más.\\n\\n¿Te gustaría iniciar con el curso y luego avanzar en la carrera? 😊",
    "Emergencias Médicas": "¡Excelente elección! 💙 En Emergencias Médicas aprenderás a evaluar pacientes, brindar soporte vital y actuar en situaciones de alto riesgo y desastres prehospitalarios.\\nSin embargo, yo te recomiendo comenzar con el curso de 8 meses, ya que es una opción económica que te brinda de 8 a 10 certificados, fortaleciendo tu hoja de vida. Este curso práctico es el primer paso hacia tu crecimiento profesional. Al terminar, puedes obtener tu Título de Tercer Nivel en solo un año más.\\n\\n¿Te gustaría iniciar con el curso y luego avanzar en la carrera? 😊",
    "Rehabilitación Física": "¡Excelente elección! 💙 En Rehabilitación Física aprenderás a evaluar el estado físico, aplicar terapias manuales y diseñar tratamientos para recuperar la movilidad de los pacientes.\\nSin embargo, yo te recomiendo comenzar con el curso de 6 meses, ya que es una opción económica que te brinda múltiples certificados, fortaleciendo tu hoja de vida. Este curso práctico es el primer paso hacia tu crecimiento profesional. Al terminar, puedes obtener tu Título de Tercer Nivel en solo un año más.\\n\\n¿Te gustaría iniciar con el curso y luego avanzar en la carrera? 😊",
    "Laboratorio Clínico": "¡Excelente elección! 💙 En Laboratorio Clínico aprenderás a procesar muestras, interpretar resultados diagnósticos e implementar normas de bioseguridad.\\nSin embargo, yo te recomiendo comenzar con el curso de 5 meses, ya que es una opción económica que te brinda múltiples certificados, fortaleciendo tu hoja de vida. Este curso práctico es el primer paso hacia tu crecimiento profesional. Al terminar, puedes obtener tu Título de Tercer Nivel de forma acelerada mediante homologación.\\n\\n¿Te gustaría iniciar con el curso y luego avanzar en la carrera? 😊",
    "Administración de Farmacias": "¡Excelente elección! 💙 En Administración de Farmacias aprenderás a gestionar medicamentos, dispensar recetas y atender al cliente con normativas de salud.\\nSin embargo, yo te recomiendo comenzar con el curso de 5 meses, ya que es una opción económica que te brinda múltiples certificados, fortaleciendo tu hoja de vida. Este curso práctico es el primer paso hacia tu crecimiento profesional. Al terminar, puedes obtener tu Título de Tercer Nivel de forma acelerada mediante homologación.\\n\\n¿Te gustaría iniciar con el curso y luego avanzar en la carrera? 😊",
    "Educación Inicial": "¡Excelente elección! 💙 En Educación Inicial aprenderás a estimular el desarrollo psicomotor, crear material didáctico y guiar el aprendizaje infantil.\\nSin embargo, yo te recomiendo comenzar con el curso de 8 meses, ya que es una opción económica que te brinda de 8 a 10 certificados, fortaleciendo tu hoja de vida. Este curso práctico es el primer paso hacia tu crecimiento profesional. Al terminar, puedes obtener tu Título de Tercer Nivel en solo un año más.\\n\\n¿Te gustaría iniciar con el curso y luego avanzar en la carrera? 😊",
    "Mecánica Automotriz": "¡Excelente elección! 💙 En Mecánica Automotriz aprenderás a diagnosticar fallas, reparar motores y trabajar con sistemas electrónicos modernos en vehículos.\\nSin embargo, yo te recomiendo comenzar con nuestros cursos cortos, ya que son una opción económica que te brinda certificados, fortaleciendo tu hoja de vida. Este curso práctico es el primer paso hacia tu crecimiento profesional. Al terminar, puedes obtener tu Título de Tercer Nivel.\\n\\n¿Te gustaría iniciar con el curso y luego avanzar en la carrera? 😊",
    "Naturopatía": "¡Excelente elección! 💙 En Naturopatía aprenderás el uso de plantas medicinales, nutrición natural y terapias alternativas para mejorar el bienestar.\\nSin embargo, yo te recomiendo comenzar con el curso de 8 meses, ya que es una opción económica que te brinda de 8 a 10 certificados, fortaleciendo tu hoja de vida. Este curso práctico es el primer paso hacia tu crecimiento profesional. Al terminar, puedes obtener tu Título de Tercer Nivel en solo un año más.\\n\\n¿Te gustaría iniciar con el curso y luego avanzar en la carrera? 😊",
}

for carrera, new_text in replacements.items():
    pattern = rf'text: "¡Excelente elección! 💙 Con la carrera de {carrera}.*?avanzar a la carrera\?"'
    replacement = f'text: "{new_text}"'
    content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    print(f"Replaced {count} instances for {carrera}")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done")
