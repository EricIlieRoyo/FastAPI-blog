from app.form.base_form import BaseForm


class CommentCreateForm(BaseForm):
    def __init__(self, author_name: str = "", content: str = ""):
        super().__init__()
        self.author_name = (author_name or "").strip()
        self.content = (content or "").strip()

    def validate(self) -> bool:
        if not self.author_name:
            self.add_error("Tu nombre o alias es obligatorio para comentar.")
        elif len(self.author_name) < 2:
            self.add_error("El nombre debe tener al menos 2 caracteres.")
        elif len(self.author_name) > 100:
            self.add_error("El nombre no puede superar los 100 caracteres.")

        if not self.content:
            self.add_error("El comentario no puede estar vacío.")
        elif len(self.content) < 3:
            self.add_error("El comentario debe tener al menos 3 caracteres.")
        elif len(self.content) > 1000:
            self.add_error("El comentario no puede exceder los 1000 caracteres.")

        return self.is_valid
