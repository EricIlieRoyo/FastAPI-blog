from app.form.base_form import BaseForm
from app.form.post_form import PostCreateForm, PostEditForm
from app.form.comment_form import CommentCreateForm
from app.form.auth_form import LoginForm, RegisterForm
from app.form.contact_form import ContactForm

__all__ = [
    "BaseForm",
    "PostCreateForm",
    "PostEditForm",
    "CommentCreateForm",
    "LoginForm",
    "RegisterForm",
    "ContactForm",
]
