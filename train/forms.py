"""all forms for Train app"""
from django.forms import ModelForm, Select, TextInput, ModelChoiceField, ModelMultipleChoiceField, CheckboxSelectMultiple

from .models import Exercise, Routine, Session, User

class SessionForm(ModelForm):
    """Create new workout session"""
    class Meta:
        model = Session
        fields = ('routine', 'trainer')
        widgets = {
            'routine': Select(attrs={'class': 'form-control'}),
            'trainer': Select(attrs={'class': 'form-control'})
        }

class ExerciseForm(ModelForm):
    """Create a new Exercise"""
    class Meta:
        model = Exercise
        fields = ('name', 'body_part')
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'body_part': Select(attrs={'class': 'form-control'})
        }

class RoutineForm(ModelForm):
    """Create a new Routine"""
    # only client users are options for this form
    client = ModelChoiceField(
            queryset=User.objects.filter(is_staff=False),
            widget=Select(attrs={'class': 'form-control'})
    )
    # exercises need to be pre-orderd by body part for form
    exercises = ModelMultipleChoiceField(
        queryset=Exercise.objects.order_by('body_part')
    )
    class Meta:
        model = Routine
        fields = ('name', 'client', 'exercises')
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
        }
