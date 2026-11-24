from django import forms

from .enums import PriorityEnum
from .models import Worker, Tag, Team, Project, Task


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


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Новый тег"}
            ),
        }


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "description", "members"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название команды",
                }
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "members": forms.SelectMultiple(
                attrs={"class": "form-control"}
            ),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "team", "deadline"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название проекта",
                }
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "team": forms.Select(
                attrs={"class": "form-control"}
            ),
            "deadline": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }


class TaskForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}),
    )
    priority = forms.ChoiceField(
        choices=[
            (priority.value, priority.value) for priority in PriorityEnum
        ],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "priority",
            "task_type",
            "deadline",
            "project",
            "tags",
            "is_completed",
        ]
        labels = {
            "name": "Название",
            "description": "Описание",
            "priority": "Приоритет",
            "task_type": "Тип задачи",
            "deadline": "Дедлайн",
            "project": "Проект",
            "tags": "Теги",
            "is_completed": "Выполнена",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Название задачи",
                }
            ),
            "task_type": forms.Select(attrs={"class": "form-select"}),
            "deadline": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "project": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.CheckboxSelectMultiple,
            "is_completed": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
