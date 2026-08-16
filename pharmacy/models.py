# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has on_delete set to the desired behavior
#   * Remove managed = False lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Appoinments(models.Model):
    id = models.BigAutoField(primary_key=True)
    appointment_id = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    appoinment_serial = models.CharField(max_length=255, blank=True, null=True)
    doctor = models.PositiveBigIntegerField(db_column='Doctor', blank=True, null=True)  # Field name made lowercase.
    schedule = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(db_comment='1:active, 0:inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'appoinments'


class Attendences(models.Model):
    id = models.BigAutoField(primary_key=True)
    emp = models.ForeignKey('EmployeePersonalDetails', models.DO_NOTHING, to_field='employee_id')
    date = models.DateField()
    in_field = models.TimeField(db_column='in')  # Field renamed because it was a Python reserved word.
    out = models.TimeField(blank=True, null=True)
    status = models.IntegerField()
    insert_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'attendences'


class Banks(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255, blank=True, null=True)
    phone = models.CharField(unique=True, max_length=255, blank=True, null=True)
    loc = models.ForeignKey('LocationInfos', models.DO_NOTHING, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'banks'


class BedCategories(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(db_comment='1:active, 0:Inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bed__categories'


class BedLists(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.ForeignKey(BedCategories, models.DO_NOTHING, db_column='category', blank=True, null=True)
    name = models.CharField(unique=True, max_length=255)
    floor = models.ForeignKey('Floors', models.DO_NOTHING, db_column='floor', blank=True, null=True)
    nursing_station = models.ForeignKey('NursingStations', models.DO_NOTHING, db_column='nursing_station', blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    price = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(db_comment='1:active, 0:Inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bed__lists'


class BedTransfers(models.Model):
    id = models.BigAutoField(primary_key=True)
    booking_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    category_id = models.PositiveBigIntegerField()
    from_bed = models.PositiveBigIntegerField()
    to_bed = models.PositiveBigIntegerField()
    transfer_date = models.DateTimeField(blank=True, null=True)
    transfer_by = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bed__transfers'


class Bookings(models.Model):
    id = models.BigAutoField(primary_key=True)
    booking_id = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    bed_category = models.PositiveBigIntegerField(blank=True, null=True)
    bed_list = models.PositiveBigIntegerField(blank=True, null=True)
    doctor = models.PositiveBigIntegerField(blank=True, null=True)
    sr_id = models.CharField(max_length=255, blank=True, null=True)
    addmission_by = models.CharField(max_length=255, blank=True, null=True)
    discharge_by = models.CharField(max_length=255, blank=True, null=True)
    adult = models.IntegerField(blank=True, null=True)
    children = models.IntegerField(blank=True, null=True)
    check_in = models.DateTimeField(blank=True, null=True)
    check_out = models.DateTimeField(blank=True, null=True)
    tran_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(db_comment='1:active, 0:Inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bookings'


class Cache(models.Model):
    key = models.CharField(primary_key=True, max_length=255)
    value = models.TextField()
    expiration = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cache'


class CacheLocks(models.Model):
    key = models.CharField(primary_key=True, max_length=255)
    owner = models.CharField(max_length=255)
    expiration = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'cache_locks'


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


class Corporates(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    discount = models.FloatField()
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'corporates'


class Departments(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    status = models.IntegerField()
    added_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'departments'


class Designations(models.Model):
    id = models.BigAutoField(primary_key=True)
    designation = models.CharField(max_length=255)
    dept = models.ForeignKey(Departments, models.DO_NOTHING)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'designations'


class DoctorInformation(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    degree = models.CharField(max_length=255, blank=True, null=True)
    chamber = models.CharField(max_length=255, blank=True, null=True)
    specialization = models.ForeignKey('Specializations', models.DO_NOTHING, db_column='specialization', blank=True, null=True)
    marketing_head = models.ForeignKey('UserInfos', models.DO_NOTHING, db_column='marketing_head', to_field='user_id', blank=True, null=True)
    status = models.IntegerField(db_comment='1:active, 0:Inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doctor__information'


class EmployeeEducationDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    emp = models.ForeignKey('EmployeePersonalDetails', models.DO_NOTHING, to_field='employee_id')
    degree = models.CharField(max_length=255)
    group = models.CharField(max_length=255, blank=True, null=True)
    institution = models.CharField(max_length=255)
    result = models.CharField(max_length=255, blank=True, null=True)
    scale = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    cgpa = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    marks = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    batch = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_education_details'


class EmployeeExperienceDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    emp = models.ForeignKey('EmployeePersonalDetails', models.DO_NOTHING, to_field='employee_id')
    company_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    company_location = models.CharField(max_length=255, blank=True, null=True, db_comment='location__infos')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_experience_details'


class EmployeeOrganizationDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    emp = models.ForeignKey('EmployeePersonalDetails', models.DO_NOTHING, to_field='employee_id')
    joining_date = models.DateField()
    joining_location = models.BigIntegerField(db_comment='location__infos')
    department = models.ForeignKey(Departments, models.DO_NOTHING, db_column='department')
    designation = models.ForeignKey(Designations, models.DO_NOTHING, db_column='designation')
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_organization_details'


class EmployeePersonalDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.OneToOneField('UserInfos', models.DO_NOTHING)
    name = models.CharField(max_length=255)
    fathers_name = models.CharField(max_length=255, blank=True, null=True)
    mothers_name = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=255)
    religion = models.CharField(max_length=255)
    marital_status = models.CharField(max_length=255)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    nid_no = models.CharField(max_length=255, blank=True, null=True)
    phn_no = models.CharField(max_length=255)
    blood_group = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255)
    location_id = models.BigIntegerField()
    tran_user_type = models.ForeignKey('TransactionWiths', models.DO_NOTHING, db_column='tran_user_type')
    address = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_personal_details'


class EmployeeTrainingDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    emp = models.ForeignKey(EmployeePersonalDetails, models.DO_NOTHING, to_field='employee_id')
    training_title = models.CharField(max_length=255)
    country = models.CharField(max_length=255, blank=True, null=True)
    topic = models.CharField(max_length=255)
    institution_name = models.CharField(max_length=255)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employee_training_details'


class FailedJobs(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.CharField(unique=True, max_length=255)
    connection = models.TextField()
    queue = models.TextField()
    payload = models.TextField()
    exception = models.TextField()
    failed_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'failed_jobs'


class Floors(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    no_of_rooms = models.IntegerField(blank=True, null=True)
    start_room_no = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(db_comment='1:active, 0:Inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'floors'


class ItemCategories(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey('TransactionMainHeads', models.DO_NOTHING, blank=True, null=True)
    category_name = models.CharField(max_length=255)
    company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, to_field='company_id', blank=True, null=True)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item__categories'


class ItemForms(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey('TransactionMainHeads', models.DO_NOTHING, blank=True, null=True)
    form_name = models.CharField(max_length=255)
    company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, to_field='company_id', blank=True, null=True)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item__forms'


class ItemManufacturers(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey('TransactionMainHeads', models.DO_NOTHING, blank=True, null=True)
    manufacturer_name = models.CharField(max_length=255)
    company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, to_field='company_id', blank=True, null=True)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item__manufacturers'


class ItemUnits(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey('TransactionMainHeads', models.DO_NOTHING, blank=True, null=True)
    unit_name = models.CharField(max_length=255)
    company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, to_field='company_id', blank=True, null=True)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'item__units'


class JobBatches(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    total_jobs = models.IntegerField()
    pending_jobs = models.IntegerField()
    failed_jobs = models.IntegerField()
    failed_job_ids = models.TextField()
    options = models.TextField(blank=True, null=True)
    cancelled_at = models.IntegerField(blank=True, null=True)
    created_at = models.IntegerField()
    finished_at = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job_batches'


class Jobs(models.Model):
    id = models.BigAutoField(primary_key=True)
    queue = models.CharField(max_length=255)
    payload = models.TextField()
    attempts = models.PositiveIntegerField()
    reserved_at = models.PositiveIntegerField(blank=True, null=True)
    available_at = models.PositiveIntegerField()
    created_at = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'jobs'


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


class LoginUsers(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(unique=True, max_length=255)
    company_user_id = models.CharField(max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    user_email = models.CharField(max_length=255, blank=True, null=True)
    user_phone = models.CharField(max_length=255, blank=True, null=True)
    user_role = models.ForeignKey('Roles', models.DO_NOTHING, db_column='user_role')
    password = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, to_field='company_id', blank=True, null=True)
    store_id = models.PositiveBigIntegerField(blank=True, null=True, db_comment='stores')
    status = models.IntegerField(db_comment='1 for Active 0 for Inactive')
    email_verified_at = models.DateTimeField(blank=True, null=True)
    remember_token = models.CharField(max_length=100, blank=True, null=True)
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'login__users'


class Migrations(models.Model):
    migration = models.CharField(max_length=255)
    batch = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'migrations'


class NursingStations(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    floor = models.FloatField()
    status = models.IntegerField(db_comment='1:active, 0:Inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nursing__stations'


class PartyPaymentReceives(models.Model):
    id = models.BigAutoField(primary_key=True)
    tran_id = models.CharField(max_length=255)
    tran_type = models.PositiveBigIntegerField(db_comment='transaction_main_heads')
    tran_method = models.CharField(max_length=255)
    invoice = models.CharField(max_length=255, blank=True, null=True)
    loc_id = models.PositiveBigIntegerField(blank=True, null=True, db_comment='location__infos')
    tran_type_with = models.ForeignKey('TransactionWiths', models.DO_NOTHING, db_column='tran_type_with', blank=True, null=True)
    tran_user = models.CharField(max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    user_phone = models.CharField(max_length=255, blank=True, null=True)
    user_address = models.CharField(max_length=255, blank=True, null=True)
    tran_groupe_id = models.PositiveBigIntegerField(blank=True, null=True)
    tran_head_id = models.PositiveBigIntegerField(blank=True, null=True)
    quantity = models.FloatField()
    bill_amount = models.FloatField()
    discount = models.FloatField()
    net_amount = models.FloatField()
    receive = models.FloatField(blank=True, null=True)
    payment = models.FloatField(blank=True, null=True)
    due = models.FloatField()
    party_amount = models.FloatField(blank=True, null=True)
    batch_id = models.CharField(max_length=255, blank=True, null=True)
    tran_date = models.DateTimeField()
    store = models.ForeignKey('Stores', models.DO_NOTHING, blank=True, null=True)
    payment_mode = models.PositiveBigIntegerField(blank=True, null=True)
    status = models.IntegerField(db_comment='1 for Active 0 for Inactive')
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'party_payment_receives'


class PasswordResetTokens(models.Model):
    email = models.CharField(primary_key=True, max_length=255)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'password_reset_tokens'


class PaymentMethods(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment__methods'


class PayrollMiddlewires(models.Model):
    id = models.BigAutoField(primary_key=True)
    emp = models.ForeignKey('UserInfos', models.DO_NOTHING, to_field='user_id')
    head_id = models.PositiveBigIntegerField(db_comment='transaction__heads')
    amount = models.FloatField()
    date = models.DateField(blank=True, null=True)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll__middlewires'


class PayrollSetups(models.Model):
    id = models.BigAutoField(primary_key=True)
    emp = models.ForeignKey('UserInfos', models.DO_NOTHING, to_field='user_id')
    head_id = models.PositiveBigIntegerField(db_comment='transaction__heads')
    amount = models.FloatField()
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payroll__setups'


class PermissionCompanies(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, to_field='company_id')
    permission = models.ForeignKey('PermissionHeads', models.DO_NOTHING)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permission__companies'


class PermissionCompanyTypes(models.Model):
    id = models.BigAutoField(primary_key=True)
    company_type = models.ForeignKey(CompanyTypes, models.DO_NOTHING)
    permission = models.ForeignKey('PermissionHeads', models.DO_NOTHING)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permission_company_types'


class PermissionHeads(models.Model):
    id = models.BigAutoField(primary_key=True)
    permission_mainhead = models.ForeignKey('PermissionMainHeads', models.DO_NOTHING, db_column='permission_mainhead')
    name = models.CharField(max_length=255)
    status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permission__heads'


class PermissionMainHeads(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permission_main_heads'


class PermissionRoles(models.Model):
    id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey('Roles', models.DO_NOTHING)
    status = models.IntegerField()
    permission = models.ForeignKey(PermissionHeads, models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permission__roles'


class PermissionRoutes(models.Model):
    id = models.BigAutoField(primary_key=True)
    permission = models.ForeignKey(PermissionHeads, models.DO_NOTHING)
    route_name = models.CharField(max_length=255)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permission__routes'


class PermissionUsers(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(LoginUsers, models.DO_NOTHING, to_field='user_id')
    permission = models.ForeignKey(PermissionHeads, models.DO_NOTHING)
    company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, to_field='company_id', blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'permission__users'


class PersonalAccessTokens(models.Model):
    id = models.BigAutoField(primary_key=True)
    tokenable_type = models.CharField(max_length=255)
    tokenable_id = models.PositiveBigIntegerField()
    name = models.CharField(max_length=255)
    token = models.CharField(unique=True, max_length=64)
    abilities = models.TextField(blank=True, null=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'personal_access_tokens'


class Roles(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roles'


class RoomFacilities(models.Model):
    id = models.BigAutoField(primary_key=True)
    room_id = models.CharField(max_length=255)
    facility_name = models.CharField(max_length=255)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'room__facilities'


class Sessions(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    user_id = models.PositiveBigIntegerField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    payload = models.TextField()
    last_activity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'sessions'


class Specializations(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    status = models.IntegerField(db_comment='1:active, 0:Inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'specializations'


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


class TransactionDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    tran_id = models.CharField(max_length=255)
    tran_type = models.BigIntegerField(db_comment='transaction_main_heads')
    tran_method = models.CharField(max_length=255)
    invoice = models.CharField(max_length=255, blank=True, null=True)
    loc_id = models.BigIntegerField(blank=True, null=True, db_comment='location_infos')
    tran_type_with = models.ForeignKey('TransactionWiths', models.DO_NOTHING, db_column='tran_type_with', blank=True, null=True)
    tran_bank = models.CharField(max_length=255, blank=True, null=True)
    tran_user = models.CharField(max_length=255, blank=True, null=True)
    ptn_id = models.CharField(max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    user_phone = models.CharField(max_length=255, blank=True, null=True)
    user_address = models.CharField(max_length=255, blank=True, null=True)
    tran_groupe_id = models.PositiveBigIntegerField(blank=True, null=True)
    tran_head_id = models.PositiveBigIntegerField(blank=True, null=True)
    quantity_actual = models.FloatField()
    quantity = models.FloatField()
    quantity_issue = models.FloatField()
    quantity_return = models.FloatField()
    unit_id = models.PositiveBigIntegerField(blank=True, null=True, db_comment='item__units')
    amount = models.FloatField(blank=True, null=True)
    tot_amount = models.FloatField(blank=True, null=True)
    discount = models.FloatField(blank=True, null=True)
    cp = models.FloatField(blank=True, null=True)
    mrp = models.FloatField(blank=True, null=True)
    receive = models.FloatField(blank=True, null=True)
    payment = models.FloatField(blank=True, null=True)
    due = models.FloatField(blank=True, null=True)
    due_col = models.FloatField(blank=True, null=True)
    due_disc = models.FloatField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    store = models.ForeignKey(Stores, models.DO_NOTHING, blank=True, null=True)
    payment_mode = models.PositiveBigIntegerField(blank=True, null=True)
    batch_id = models.CharField(max_length=255, blank=True, null=True)
    booking_id = models.CharField(max_length=255, blank=True, null=True)
    tran_date = models.DateTimeField()
    status = models.IntegerField(db_comment='1 for Active 0 for Inactive')
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction__details'


class TransactionDetailsTemps(models.Model):
    id = models.BigAutoField(primary_key=True)
    tran_id = models.CharField(max_length=255)
    tran_type = models.BigIntegerField(db_comment='transaction_main_heads')
    tran_method = models.CharField(max_length=255)
    invoice = models.CharField(max_length=255, blank=True, null=True)
    loc_id = models.BigIntegerField(blank=True, null=True, db_comment='location_infos')
    tran_type_with = models.ForeignKey('TransactionWiths', models.DO_NOTHING, db_column='tran_type_with', blank=True, null=True)
    tran_user = models.CharField(max_length=255, blank=True, null=True)
    ptn_id = models.CharField(max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    user_phone = models.CharField(max_length=255, blank=True, null=True)
    user_address = models.CharField(max_length=255, blank=True, null=True)
    tran_groupe_id = models.PositiveBigIntegerField(blank=True, null=True)
    tran_head_id = models.PositiveBigIntegerField(blank=True, null=True)
    quantity_actual = models.FloatField()
    quantity = models.FloatField()
    quantity_issue = models.FloatField()
    quantity_return = models.FloatField()
    unit_id = models.PositiveBigIntegerField(blank=True, null=True, db_comment='item_units')
    amount = models.FloatField(blank=True, null=True)
    tot_amount = models.FloatField(blank=True, null=True)
    discount = models.FloatField(blank=True, null=True)
    cp = models.FloatField(blank=True, null=True)
    mrp = models.FloatField(blank=True, null=True)
    receive = models.FloatField(blank=True, null=True)
    payment = models.FloatField(blank=True, null=True)
    due = models.FloatField(blank=True, null=True)
    due_col = models.FloatField(blank=True, null=True)
    due_disc = models.FloatField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    store = models.ForeignKey(Stores, models.DO_NOTHING, blank=True, null=True)
    payment_mode = models.PositiveBigIntegerField(blank=True, null=True)
    batch_id = models.CharField(max_length=255, blank=True, null=True)
    booking_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    tran_date = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction__details__temps'


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


class TransactionHeads(models.Model):
    id = models.BigAutoField(primary_key=True)
    tran_head_name = models.CharField(max_length=255)
    groupe = models.ForeignKey(TransactionGroupes, models.DO_NOTHING)
    category = models.ForeignKey(ItemCategories, models.DO_NOTHING, blank=True, null=True)
    manufacturer = models.ForeignKey(ItemManufacturers, models.DO_NOTHING, blank=True, null=True)
    form = models.ForeignKey(ItemForms, models.DO_NOTHING, blank=True, null=True)
    unit = models.ForeignKey(ItemUnits, models.DO_NOTHING)
    quantity = models.FloatField()
    cp = models.FloatField()
    mrp = models.FloatField()
    expiry_date = models.DateField(blank=True, null=True)
    editable = models.IntegerField()
    company = models.ForeignKey(CompanyDetails, models.DO_NOTHING, to_field='company_id', blank=True, null=True)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction__heads'


class TransactionMainHeads(models.Model):
    id = models.BigAutoField(primary_key=True)
    type_name = models.CharField(max_length=255)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction__main__heads'


class TransactionMains(models.Model):
    id = models.BigAutoField(primary_key=True)
    tran_id = models.CharField(unique=True, max_length=255)
    tran_type = models.BigIntegerField(db_comment='transaction_main_heads')
    tran_method = models.CharField(max_length=255)
    invoice = models.CharField(max_length=255, blank=True, null=True)
    loc_id = models.BigIntegerField(blank=True, null=True, db_comment='location__infos')
    tran_type_with = models.ForeignKey('TransactionWiths', models.DO_NOTHING, db_column='tran_type_with', blank=True, null=True)
    tran_bank = models.CharField(max_length=255, blank=True, null=True)
    tran_user = models.CharField(max_length=255, blank=True, null=True)
    ptn_id = models.CharField(max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    user_phone = models.CharField(max_length=255, blank=True, null=True)
    user_address = models.CharField(max_length=255, blank=True, null=True)
    bill_amount = models.FloatField(blank=True, null=True)
    discount = models.FloatField()
    net_amount = models.FloatField(blank=True, null=True)
    receive = models.FloatField(blank=True, null=True)
    payment = models.FloatField(blank=True, null=True)
    due = models.FloatField(blank=True, null=True)
    due_col = models.FloatField(blank=True, null=True)
    due_disc = models.FloatField(blank=True, null=True)
    store = models.ForeignKey(Stores, models.DO_NOTHING, blank=True, null=True)
    payment_mode = models.PositiveBigIntegerField(blank=True, null=True)
    booking_id = models.CharField(max_length=255, blank=True, null=True)
    tran_date = models.DateTimeField()
    status = models.IntegerField(db_comment='1 for Active 0 for Inactive')
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction__mains'


class TransactionMainsTemps(models.Model):
    id = models.BigAutoField(primary_key=True)
    tran_id = models.CharField(unique=True, max_length=255)
    tran_type = models.BigIntegerField(db_comment='transaction_main_heads')
    tran_method = models.CharField(max_length=255)
    invoice = models.CharField(max_length=255, blank=True, null=True)
    loc_id = models.BigIntegerField(blank=True, null=True, db_comment='location_infos')
    tran_type_with = models.ForeignKey('TransactionWiths', models.DO_NOTHING, db_column='tran_type_with', blank=True, null=True)
    tran_user = models.CharField(max_length=255, blank=True, null=True)
    ptn_id = models.CharField(max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    user_phone = models.CharField(max_length=255, blank=True, null=True)
    user_address = models.CharField(max_length=255, blank=True, null=True)
    bill_amount = models.FloatField(blank=True, null=True)
    discount = models.FloatField()
    net_amount = models.FloatField(blank=True, null=True)
    receive = models.FloatField(blank=True, null=True)
    payment = models.FloatField(blank=True, null=True)
    due = models.FloatField(blank=True, null=True)
    due_col = models.FloatField(blank=True, null=True)
    due_disc = models.FloatField(blank=True, null=True)
    store = models.ForeignKey(Stores, models.DO_NOTHING, blank=True, null=True)
    payment_mode = models.PositiveBigIntegerField(blank=True, null=True)
    booking_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    tran_date = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction__mains__temps'


class TransactionWiths(models.Model):
    id = models.BigAutoField(primary_key=True)
    tran_with_name = models.CharField(max_length=255)
    user_role = models.BigIntegerField(db_comment='roles')
    tran_type = models.BigIntegerField(db_comment='transaction_main_heads')
    tran_method = models.CharField(max_length=255)
    status = models.IntegerField()
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'transaction__withs'


class UserInfos(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(unique=True, max_length=255)
    login_user_id = models.CharField(max_length=255, blank=True, null=True, db_comment='login__users')
    title = models.CharField(max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    user_email = models.CharField(max_length=255, blank=True, null=True)
    user_phone = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    loc_id = models.BigIntegerField(blank=True, null=True, db_comment='locations')
    user_role = models.BigIntegerField(db_comment='roles')
    tran_user_type = models.ForeignKey(TransactionWiths, models.DO_NOTHING, db_column='tran_user_type', blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    religion = models.CharField(max_length=255, blank=True, null=True)
    nid = models.CharField(max_length=255, blank=True, null=True)
    passport = models.CharField(max_length=255, blank=True, null=True)
    driving_lisence = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    corporate_id = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    store = models.ForeignKey(Stores, models.DO_NOTHING, blank=True, null=True)
    company_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(db_comment='1 for Active 0 for Inactive')
    added_at = models.DateTimeField()
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table='user__infos'
