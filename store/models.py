from django.db import models

# Create your models here.

class Stores(models.Model):
    id = models.BigAutoField(primary_key=True)
    store_name = models.CharField(max_length=255)
    division = models.CharField(max_length=255)
    location_id = models.PositiveBigIntegerField(db_comment='location__infos')
    address = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(db_comment='1 for Active 0 for Inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stores'

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