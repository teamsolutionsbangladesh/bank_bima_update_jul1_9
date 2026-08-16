from django.db import models

# Create your models here.
class LocationInfos(models.Model):
    id = models.BigAutoField(primary_key=True)
    division = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    upazila = models.CharField(max_length=255)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'location__infos'