from app.form.base_form import BaseForm


class ContactForm(BaseForm):
    def __init__(
        self,
        name: str = "",
        email: str = "",
        subject: str = "",
        message: str = ""
    ):
        super().__init__()
        self.name = (name or "").strip()
        self.email = (email or "").strip().lower()
        self.subject = (subject or "").strip()
        self.message = (message or "").strip()

    def validate(self) -> bool:
        if not self.name:
            self.add_error("El nombre es obligatorio.")
        elif len(self.name) < 2:
            self.add_error("El nombre debe tener al menos 2 caracteres.")

        if not self.email:
            self.add_error("El correo o Gmail es obligatorio.")
        elif "@" not in self.email or "." not in self.email:
            self.add_error("Introduce un correo o Gmail válido.")

        if not self.subject:
            self.add_error("El asunto es obligatorio.")
        elif len(self.subject) < 3:
            self.add_error("El asunto debe tener al menos 3 caracteres.")

        if not self.message:
            self.add_error("El comentario o mensaje es obligatorio.")
        elif len(self.message) < 5:
            self.add_error("El comentario debe tener al menos 5 caracteres.")

        return self.is_valid
