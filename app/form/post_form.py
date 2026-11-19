from app.form.base_form import BaseForm
from app.utils import slugify


class PostCreateForm(BaseForm):
    def __init__(
        self,
        title: str = "",
        author: str = "",
        content: str = "",
        image_url: str = "",
        in_carousel: bool = False
    ):
        super().__init__()
        self.title = (title or "").strip()
        self.author = (author or "").strip()
        self.content = (content or "").strip()
        self.image_url = (image_url or "").strip()
        self.in_carousel = bool(in_carousel)
        self.slug: str = ""

    def validate(self) -> bool:
        if not self.title:
            self.add_error("El título es obligatorio.")
        elif len(self.title) < 3:
            self.add_error("El título debe tener al menos 3 caracteres.")
        elif len(self.title) > 200:
            self.add_error("El título no puede exceder los 200 caracteres.")

        if not self.author:
            self.add_error("El nombre del autor es obligatorio.")
        elif len(self.author) < 2:
            self.add_error("El autor debe tener al menos 2 caracteres.")
        elif len(self.author) > 100:
            self.add_error("El autor no puede exceder los 100 caracteres.")

        if not self.content:
            self.add_error("El contenido del post es obligatorio.")
        elif len(self.content) < 10:
            self.add_error("El contenido debe tener al menos 10 caracteres.")

        if self.is_valid:
            self.slug = slugify(self.title)

        return self.is_valid


class PostEditForm(BaseForm):
    def __init__(
        self,
        title: str = "",
        author: str = "",
        content: str = "",
        image_url: str = "",
        in_carousel: bool = False
    ):
        super().__init__()
        self.title = (title or "").strip()
        self.author = (author or "").strip()
        self.content = (content or "").strip()
        self.image_url = (image_url or "").strip()
        self.in_carousel = bool(in_carousel)

    def validate(self) -> bool:
        if not self.title:
            self.add_error("El título no puede estar vacío.")
        elif len(self.title) < 3:
            self.add_error("El título debe tener al menos 3 caracteres.")
        elif len(self.title) > 200:
            self.add_error("El título no puede exceder los 200 caracteres.")

        if not self.author:
            self.add_error("El autor no puede estar vacío.")

        if not self.content:
            self.add_error("El contenido no puede estar vacío.")
        elif len(self.content) < 10:
            self.add_error("El contenido debe tener al menos 10 caracteres.")

        return self.is_valid
