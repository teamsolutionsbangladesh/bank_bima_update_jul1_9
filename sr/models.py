from django.db import models

class SalesRepresentative(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'item__sr_agents'  # Mapped to exact backend lookup configuration database tracking target name

    def __str__(self):
        return f"[ID: {self.id}] {self.name}"