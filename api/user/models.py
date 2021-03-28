from django.db import models
import uuid

# Create your models here.

class User(models.Model):

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=255)
    country = models.CharField(max_length=255, default='tr')
    points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    country_rank = models.IntegerField(default=0)


    class Meta:
        ordering = ['points']

    def __repr__(self):
        return str(self.user_id)