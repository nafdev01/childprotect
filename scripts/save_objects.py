import csv
from safesearch.models import SearchAlert

def run():
    my_objects = SearchAlert.objects.all()
    for my_object in my_objects:
        my_object.save()
        