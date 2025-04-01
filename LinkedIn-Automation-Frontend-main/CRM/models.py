from django.db import models
from django.db.models import JSONField
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField



class Linkedin_user(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,  null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    cookies = models.TextField(null=True, blank=True)

class SavedSearch(models.Model):
    linkedinuser = models.ForeignKey("Linkedin_user", on_delete=models.CASCADE)
    link = models.TextField()
    name = models.TextField()

class LeadsList(models.Model):
    linkedinuser = models.ForeignKey("Linkedin_user", on_delete=models.CASCADE)
    link = models.TextField()
    name = models.TextField()


class ScrapperProxy(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,  null=True, blank=True)
    proxyip = models.CharField(max_length=255)
    proxyport = models.CharField(max_length=255)
    proxyuser = models.CharField(max_length=255)
    proxypass = models.CharField(max_length=255)

class Account(models.Model):
    name = models.CharField(max_length=255)
    cookies = models.TextField()
    proxyip = models.CharField(max_length=255)
    proxyport = models.CharField(max_length=255)
    proxyuser = models.CharField(max_length=255)
    proxypass = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default="Paused")
    restrict_view = models.CharField(max_length=255, default="enabled")
    capacity_limit = models.IntegerField(null=True, blank=True)





class Campaign(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateTimeField()  # changed to DateTimeField
    end_date = models.DateTimeField()
    job_title = models.CharField(max_length=255, null=True, blank=True)
    connects_sent= models.IntegerField(null=True, blank=True)
    connect_accepted = models.IntegerField(null=True, blank=True)
    account = models.ForeignKey("Account", on_delete=models.CASCADE, null=True, blank=True)
    daily_count= models.IntegerField(null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    search_value = models.CharField(max_length=255, null=True, blank=True)
    boolean_search = models.TextField(null=True, blank=True)
    min_salary= models.IntegerField(null=True, blank=True)
    max_salary= models.IntegerField(null=True, blank=True)
    min_age= models.IntegerField(null=True, blank=True)
    max_age= models.IntegerField(null=True, blank=True)
    min_experience= models.IntegerField(null=True, blank=True)
    max_experience= models.IntegerField(null=True, blank=True)
    batch_size = models.IntegerField(null=True, blank=True)
    total_profile_count = models.IntegerField(null=True, blank=True)
    status= models.CharField(max_length=20,default='pending', null=True, blank=True)
    include_nationality_list = ArrayField(models.CharField(max_length=1026), blank=True, null=True)
    nationality_batch = models.IntegerField(null=True, blank=True)
    exclude_nationality_list = ArrayField(models.CharField(max_length=1026), blank=True, null=True)
    include_first_names_list = ArrayField(models.CharField(max_length=1026), blank=True, null=True)
    exclude_first_names_list = ArrayField(models.CharField(max_length=1026), blank=True, null=True)
    expat = models.BooleanField(default=False, null=True, blank=True)
    local = models.BooleanField(default=False, null=True, blank=True)
    autoscrapper = models.BooleanField(default=False, null=True, blank=True)
    saved_search = models.ForeignKey("SavedSearch", on_delete=models.CASCADE, null=True, blank=True)
    lead_list = models.ForeignKey("LeadsList", on_delete=models.CASCADE, null=True, blank=True)

    minpage = models.IntegerField(null=True, blank=True)
    maxpage = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    gpt_prompt = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.name 
class Excel_file(models.Model):
    campaign = models.ForeignKey("Campaign", on_delete=models.CASCADE, null =True, blank = True)
    created_at = models.DateTimeField(default=timezone.now, null =True, blank = True)  # changed to DateTimeField
    json_data = JSONField()
    name = models.CharField(max_length=255, null=True, blank=True)
    duplicate =  models.BooleanField(default=False, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,  null=True, blank=True)

class Connections(models.Model):
    campaign = models.ForeignKey("Campaign", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)

class Profile(models.Model):
    campaign = models.ForeignKey("Campaign", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=255, null=True, blank=True)
    intro_message = models.TextField(null=True, blank=True)
    last_communication = models.DateTimeField(null=True, blank=True)
    jd_status = models.BooleanField(default=False, null=True, blank=True)
    redirected_link = models.CharField(max_length=512, null=True, blank=True)
    headline = models.CharField(max_length=512, null=True, blank=True)
    location = models.CharField(max_length=512, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    expat_status = models.BooleanField(blank=True, null=True)
    gender = models.CharField(max_length=12, null=True, blank=True)
    lead_status = models.CharField(max_length=512, null=True, blank=True)
    lead_last_contact = models.DateTimeField( null =True, blank = True)

class Skill(models.Model):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)

class Experience(models.Model):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    time_spent = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)

class Education(models.Model):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    institute = models.CharField(max_length=255, null=True, blank=True)
    education = models.CharField(max_length=255, null=True, blank=True)

class Message(models.Model):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    message = models.CharField(max_length=255)

class PromptManagement(models.Model):
    value = models.CharField(max_length=255)
    prompt = models.TextField()

class UserMetricsDistribution(models.Model):
    account = models.ForeignKey("Account", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,  null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null =True, blank = True) 


class ScrapperLogs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,  null=True, blank=True)
    search_time = models.DateTimeField(default=timezone.now, null =True, blank = True) 
    category = models.CharField(max_length=255, null=True, blank=True)
    leads_extracted = models.IntegerField(null=True, blank=True)


class Note(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)







