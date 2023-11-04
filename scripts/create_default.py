import csv
from safesearch.models import BannedDefault, BanReason
from django.db.utils import IntegrityError


DEFAULT_DICTIONARY = {
    "adult": BanReason.ADULT_CONTENT,
    "violent": BanReason.VIOLENT_AND_DISTURBING_CONTENT,
    "drugs": BanReason.DRUGS,
    "offensive": BanReason.OFFENSIVE_LANGUAGE,
}


def run():
    # Open the CSV file in read mode

    for key, value in DEFAULT_DICTIONARY.items():
        with open(f"static/csv_files/{key}.csv", mode="r") as file:
            print(f"Creating {key} default banned words ....")
            counter = 0
            # Create a CSV reader
            csv_reader = csv.reader(file)

            # Iterate through the rows in the CSV file
            for row in csv_reader:
                # Output each word on a new line
                for word in row:
                    if word.strip() == "":
                        continue
                    # Create a new BannedDefault object
                    try:
                        banned_default = BannedDefault.objects.create(
                            word=word, category=value
                        )
                        banned_default.save()
                        counter += 1
                    except IntegrityError:
                        print(f"{word} already exists in the database")
            print(f"Created {counter} {key} default banned words!\n")
