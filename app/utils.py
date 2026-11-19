import re
import unicodedata


def slugify(text: str) -> str:
    """
    Convierte una cadena de texto en un slug amigable para URLs.
    Ejemplo: '¡Hola, Mundo en FastAPI!' -> 'hola-mundo-en-fastapi'
    """
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", text)
