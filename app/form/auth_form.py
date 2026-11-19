from app.form.base_form import BaseForm


class LoginForm(BaseForm):
    def __init__(self, username: str = "", password: str = ""):
        super().__init__()
        self.username = (username or "").strip()
        self.password = (password or "").strip()

    def validate(self) -> bool:
        if not self.username:
            self.add_error("El nombre de usuario es obligatorio.")
        if not self.password:
            self.add_error("La contraseña es obligatoria.")
        return self.is_valid


class RegisterForm(BaseForm):
    def __init__(
        self,
        username: str = "",
        email: str = "",
        password: str = "",
        confirm_password: str = ""
    ):
        super().__init__()
        self.username = (username or "").strip()
        self.email = (email or "").strip().lower()
        self.password = (password or "").strip()
        self.confirm_password = (confirm_password or "").strip()

    def validate(self) -> bool:
        if not self.username:
            self.add_error("El nombre de usuario es obligatorio.")
        elif len(self.username) < 3:
            self.add_error("El nombre de usuario debe tener al menos 3 caracteres.")
        elif len(self.username) > 30:
            self.add_error("El nombre de usuario no puede superar los 30 caracteres.")

        if not self.email:
            self.add_error("El correo electrónico es obligatorio.")
        elif "@" not in self.email or "." not in self.email:
            self.add_error("Por favor ingresa un correo electrónico válido.")

        if not self.password:
            self.add_error("La contraseña es obligatoria.")
        elif len(self.password) < 6:
            self.add_error("La contraseña debe tener al menos 6 caracteres.")

        if self.password != self.confirm_password:
            self.add_error("Las contraseñas no coinciden.")

        return self.is_valid
