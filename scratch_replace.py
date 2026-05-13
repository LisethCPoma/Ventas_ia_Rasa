import sys
import re

file_path = 'actions/actions.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace imports
if 'import os' not in content:
    content = content.replace('import google.generativeai as genai', 'import os\nfrom dotenv import load_dotenv\nimport google.generativeai as genai')

# Replace api_keys array
pattern = re.compile(r'# 3\. Lista de tus API Keys \(Rotador\)\s+# Reemplaza estos textos con tus 10 API keys reales\s+api_keys = \[\s+.*?\]', re.DOTALL)

replacement = """# 3. Lista de tus API Keys (Rotador)
        # Cargamos las API keys desde las variables de entorno (.env)
        load_dotenv()
        api_keys_str = os.getenv("GEMINI_API_KEYS", "")
        api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
        
        if not api_keys:
            print("ADVERTENCIA: No se encontraron API keys en el archivo .env. Asegúrate de configurar GEMINI_API_KEYS.")"""

content = pattern.sub(replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("actions.py updated successfully.")
