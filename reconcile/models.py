from django.db import models
class Location(models.Model):
    location_id=models.CharField(max_length=20,unique=True)
    org_id=models.CharField(max_length=20)
    name=models.CharField(max_length=100,blank=True)
    def __str__(self): return f"{self.location_id} ({self.org_id})"
class SystemARecord(models.Model):
    record_id=models.CharField(max_length=20,unique=True)
    location=models.ForeignKey(Location,on_delete=models.PROTECT,related_name='a_records')
    event_date=models.DateField(null=True,blank=True)
    category_code=models.CharField(max_length=20,blank=True)
    actor_id=models.CharField(max_length=20,null=True,blank=True)  # blank in CSV -> NULL, row kept
    base_value=models.DecimalField(max_digits=18,decimal_places=2,null=True,blank=True)
    adjustment=models.DecimalField(max_digits=18,decimal_places=2,null=True,blank=True)
    total_value=models.DecimalField(max_digits=18,decimal_places=2,null=True,blank=True)
    state=models.CharField(max_length=20,default='CONFIRMED')
class SystemBEntry(models.Model):
    entry_id=models.CharField(max_length=30,unique=True)
    record_ref_raw=models.CharField(max_length=30,blank=True)  # original text, never lost
    record_ref=models.CharField(max_length=20,null=True,blank=True)  # cleaned REC-xxxx
    location=models.ForeignKey(Location,on_delete=models.PROTECT,related_name='b_entries')
    recorded_on=models.DateField(null=True,blank=True)
    value_raw=models.CharField(max_length=50,blank=True)
    value=models.DecimalField(max_digits=18,decimal_places=2,null=True,blank=True)  # blank -> NULL, never 0
    label=models.CharField(max_length=100,blank=True)
    # No FK to SystemARecord: orphans (e.g. REC-1999) would be rejected by the DB.
