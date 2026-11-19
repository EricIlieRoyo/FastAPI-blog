from typing import List, Dict, Any


class BaseForm:
    """
    Clase base para la validación y manejo de formularios HTML.
    Mantiene los errores y los datos enviados para repoblar la vista en caso de error.
    """

    def __init__(self):
        self.errors: List[str] = []

    def add_error(self, message: str):
        self.errors.append(message)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
