"""Models for Personal Training App"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Client, Trainer, or Admin user"""
    user_choices = [('CL', 'client'), ('TR', 'trainer'), ('AD', 'admin')]

    def __str__(self):
        return f"{self.first_name}"

class Exercise(models.Model):
    """Exercise such as plank, squat, row"""
    body_choices = [
        ('LE', 'Legs'),
        ('AR', 'Arms'),
        ('BA', 'Back'),
        ('CH', 'Chest'),
        ('SH', 'Shoulders'),
        ('CO', 'Core'),
        ('OT', 'Other')
    ]
    name = models.CharField(max_length=40, unique=True)
    body_part = models.CharField(max_length=2, choices=body_choices)

    def __str__(self):
        return self.name

class Routine(models.Model):
    """A group of exercises for a particular user"""
    name = models.CharField(max_length=20, verbose_name='Routine Name')
    startdate = models.DateField(auto_now_add=True)
    client = models.ForeignKey("User", on_delete=models.CASCADE, related_name="routines",
                              limit_choices_to={'is_staff': 'False'})
    exercises = models.ManyToManyField("Exercise", related_name="routines")
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client.first_name}'s {self.name}"

class Setgroup(models.Model):
    """Series of sets for a specicic excercise in a specific routine"""
    exercise = models.ForeignKey("Exercise", on_delete=models.PROTECT, related_name="setgroups")
    session = models.ForeignKey("Session", on_delete=models.CASCADE, related_name="setgroups")
    note = models.CharField(max_length=50, blank=True, null=True)
    order = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.exercise.name} Sets"

class Set(models.Model):
    """One set of an exercise performed by one user one time"""
    num_choices = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5")
    ]
    setgroup = models.ForeignKey("Setgroup", on_delete=models.CASCADE, related_name="sets")
    setnum = models.IntegerField(choices=num_choices, verbose_name='Set')
    weight = models.CharField(max_length=20)
    time = models.CharField(max_length=15)

    def __str__(self):
        return f"set {self.setnum} of {self.setgroup.exercise.name}"

    def serialize(self):
        """serialize Sets for API request"""
        return {
            "date": self.setgroup.session.timestamp.astimezone().strftime("%b %-d %Y, %-I:%M %p"),
            "weight": self.weight,
            "time": self.time
        }

class Session(models.Model):
    """A collection of setgroups by a user on a given day (e.g. a workout)"""
    routine = models.ForeignKey("Routine", on_delete=models.PROTECT, related_name="sessions",
                                limit_choices_to={'archived': 'False'})
    timestamp = models.DateTimeField(auto_now_add=True)
    trainer = models.ForeignKey("User", on_delete=models.SET_NULL, null=True,
                                limit_choices_to={'is_staff': 'True', 'is_superuser': 'False'})

    def __str__(self):
        return f"Session {self.pk} by {self.trainer.first_name} - {self.routine.name}"

    def serialize(self):
        """serialize Sessions for API request"""
        return {
            "pk": self.pk,
            "trainer": self.trainer.first_name,
            "client": self.routine.client.first_name,
            "routine": self.routine.name,
            "timestamp": self.timestamp.astimezone().strftime("%b %-d %Y, %-I:%M %p")
        }
