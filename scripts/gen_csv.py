import csv
from faker import Faker
import random

# Create an instance of the Faker class
fake = Faker()

# Number of words and phrases to generate in the row
num_entries = 300

# Define the CSV file name
csv_file = "fake_words_and_phrases.csv"

# Generate fake words and phrases and write them to the CSV file
with open(csv_file, "w", newline="") as file:
    writer = csv.writer(file)

    fake_entries = []

    for i in range(num_entries):
        if i % 2 == 0:
            # Even index, generate a phrase
            word_len = random.randint(2, 4)
            phrase = fake.sentence(word_len)
            fake_entries.append(phrase[:-1])
        else:
            # Odd index, generate a single word
            word = fake.word()
            fake_entries.append(word)

    # Write the row of fake words and phrases to the CSV file
    writer.writerow(fake_entries)

print(f"A row of {num_entries} fake words and phrases has been written to {csv_file}.")
