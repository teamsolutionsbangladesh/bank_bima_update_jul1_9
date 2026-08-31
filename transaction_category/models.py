from django.db import models

# Create your models here.
class ItemCategory(models.Model):
    type_id = models.CharField(max_length=50, blank=True, null=True)
    group_id = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, default='Active')

    def __str__(self):
        return self.name if self.name else f"Category {self.id}"