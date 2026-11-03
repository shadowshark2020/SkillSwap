import re

# Lista base de palabras prohibidas (puedes ampliarla según necesites)
FORBIDDEN_WORDS = [
    # Insultos y groserías generales / comunes
    "puta", "puto", "mierda", "carajo", "pendejo", "pendeja", 
    "cabrón", "cabron", "imbécil", "imbecil", "estúpido", "estupido", 
    "idiota", "estiercol", "gilipollas", "maricón", "maricon", 
    "culero", "chingada", "chingar", "chingado", "verga", "pito", 
    "coño", "huevón", "huevon", "boludo", "pelotudo", "cagada", 
    "cagar", "mamón", "mamon", "zorrra", "zorra", "chupada",
    "imbecil", "idiota", "tarado", "estupidez"
]

def bot_check_content(text):
    text_lower = text.lower()
    for word in FORBIDDEN_WORDS:
        if re.search(r'\b' + word + r'\b', text_lower):
            return True # Detectó contenido prohibido
    return False