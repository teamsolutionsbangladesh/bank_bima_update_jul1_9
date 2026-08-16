# doctors/models.py
from django.db import models

class Doctor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    chamber = models.CharField(max_length=255, blank=True, null=True)
    doctor_type = models.CharField(max_length=20, default='diagnosis')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'doctors_doctor'  # Explicit clean database routing map context alignment target tag

    def __str__(self):
        return f"[ID: {self.id}] {self.name}"