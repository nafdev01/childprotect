import csv
from safesearch.models import BannedDefault, BanReason
from django.db.utils import IntegrityError


def run():
    counter = 0
    # Open the CSV file in read mode
    with open("static/csv_files/shopping.csv", mode="r") as file:
        # Create a CSV reader
        csv_reader = csv.reader(file)

        # Iterate through the rows in the CSV file
        for row in csv_reader:
            # Output each word on a new line
            for word in row:
                # Create a new BannedDefault object
                try:
                    banned_default = BannedDefault.objects.create(
                        word=word, category=BanReason.SHOPPING
                    )
                    banned_default.save()
                    counter += 1
                except IntegrityError:
                    print(f"{word} already exists in the database")
