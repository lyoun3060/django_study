from django.db import models
from datetime import datetime
from sklearn.semi_supervised import _self_training

# Create your models here.
class Board(models.Model):
    bno=models.AutoField(primary_key=True) #autoincresement
    writer = models.CharField(null=False, max_length=50)
    title=models.CharField(null=False, max_length=120)
    content=models.TextField(null=False)
    hit=models.IntegerField(default=0)
    post_date=models.DateTimeField(default=datetime.now, blank=True)
    filename=models.CharField(null=True, blank=True, default='', max_length=500)
    filesize=models.IntegerField(default=0)
    down=models.IntegerField(default=0)
    
    def hit_up(self):
        self.hit+=1
    
    def down_up(self):
        self.down+=1
        
class Comment(models.Model):
    cno=models.AutoField(primary_key=True)
    bno=models.IntegerField(null=False)
    wiriter=models.CharField(null=False, max_length=50)
    content=models.TextField(null=False)
    post_date=models.DateTimeField(default=datetime.now, blank=True)
    