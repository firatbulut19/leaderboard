from django.db import models
import uuid

# Create your models here.

class User(models.Model):

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=255)
    country = models.CharField(max_length=255, default='tr')
    points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)

    class Meta:
        ordering = ['points']

    def get_points(self):
        return self.display_name + ' has ' + str(self.points) + ' points.'

    def get_rank(self):
        return self.display_name + ' is rank ' + str(self.rank) + '.'

    def __repr__(self):
        return self.display_name + ' is added.'