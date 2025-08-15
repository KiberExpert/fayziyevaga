from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.
class BaseModel(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

# biz haqimizda
class Course(BaseModel):
    image=models.FileField(upload_to='course/', null=True)
    name = models.CharField(max_length=500)
    def __str__(self):
        return self.name
    
class Thema(BaseModel):
    name = models.CharField(max_length=500)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.name + '-' + self.course.name

class Maruza(BaseModel):
    name = models.CharField(max_length=500)
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, null=True)
    description = RichTextField()
    file=models.CharField(max_length=500, null=True)
    def __str__(self):
        return self.name + '-' + self.thema.name

class Video(BaseModel):
    name = models.CharField(max_length=500)
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, null=True)
    url = models.CharField(max_length=500)
    def __str__(self):
        return self.name + '-' + self.thema.name

class Taqdimot(BaseModel):
    name = models.CharField(max_length=500)
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, null=True)
    description = RichTextField()
    file=models.CharField(max_length=500, null=True)
    def __str__(self):
        return self.name + '-' + self.thema.name

class TestName(BaseModel):
    name = models.CharField(max_length=500)
    thema = models.ForeignKey(Thema, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.name + '-' + self.thema.name

class Test(BaseModel):
    name = models.CharField(max_length=500)
    test_name = models.ForeignKey(TestName, on_delete=models.CASCADE, null=True)
    key1 = RichTextField()
    key2 = RichTextField()
    key3 = RichTextField()
    key4 = RichTextField()
    def __str__(self):
        return self.name + '-' + self.test_name.name

class Role(BaseModel):
    name = models.CharField(max_length=500)
    def __str__(self):
        return self.name

class User(BaseModel):
    fullname = models.CharField(max_length=500)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    login = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=50, null=True)
    def __str__(self):
        return self.fullname + '-' + self.role.name
    
class MaruzaLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    maruza = models.ForeignKey(Maruza, on_delete=models.CASCADE, null=True)
    status=models.BooleanField(default=False)
    def __str__(self):
        return self.user.fullname + '-' + self.maruza.name

class VideoLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True)
    status=models.BooleanField(default=False)
    def __str__(self):
        return self.user.fullname + '-' + self.video.name

class TaqdimotLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    taqdimot = models.ForeignKey(Taqdimot, on_delete=models.CASCADE, null=True)
    status=models.BooleanField(default=False)
    def __str__(self):
        return self.user.fullname + '-' + self.taqdimot.name
    
class TestLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    test = models.ForeignKey(TestName, on_delete=models.CASCADE, null=True)
    status=models.BooleanField(default=False)
    def __str__(self):
        return self.user.fullname + '-' + self.test.name

class GetCerftificate(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    status=models.BooleanField(default=False)
    def __str__(self):
        return self.user.fullname + '-' + self.course.name



