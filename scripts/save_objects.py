import csv
from safesearch.models import FlaggedAlert

def run():
    my_objects = FlaggedAlert.objects.all()
    for my_object in my_objects:
        my_object.save()
        