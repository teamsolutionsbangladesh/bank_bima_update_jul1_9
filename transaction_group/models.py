from django.db import models

# Create your models here.
class CompanyDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    company_id = models.CharField(unique=True, max_length=255)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_email = models.CharField(unique=True, max_length=255, blank=True, null=True)
    company_phone = models.CharField(unique=True, max_length=255, blank=True, null=True)
    company_type = models.ForeignKey('CompanyTypes', models.DO_NOTHING, db_column='company_type', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(db_comment='1 for Active 0 for Inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company__details'
class CompanyTypes(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company__types'
class TransactionGroupes(models.Model):
    id = models.BigAutoField(primary_key=True)
    tran_groupe_name = models.CharField(max_length=255)
    tran_groupe_type = models.ForeignKey('TransactionMainHeads', models.DO_NOTHING, db_column='tran_groupe_type')
    tran_method = models.CharField(max_length=255)
    company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, to_field='company_id', blank=True, null=True)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction__groupes'
class TransactionMainHeads(models.Model):
    id = models.BigAutoField(primary_key=True)
    type_name = models.CharField(max_length=255)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction__main__heads'
