from django import forms

from .models import Worker


class WorkerUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Новый пароль",
        required=False,
        min_length=8,
        max_length=12,
        widget=forms.PasswordInput,
        help_text=(
            "Оставьте поле пустым, чтобы не менять. "
            "Минимум 8, максимум 12 символов"
        ),
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        required=False,
        min_length=8,
        max_length=12,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = Worker
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "position",
        ]

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if (password1 or password2) and password1 != password2:
            self.add_error("password2", "Пароли не совпадают")
        return cleaned_data

    def save(self, commit=True):
        worker = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            worker.set_password(password)
        if commit:
            worker.save()
        return worker
