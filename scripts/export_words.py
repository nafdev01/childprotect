import csv
from safesearch.models import BannedWord

def run():
    banned_words = BannedWord.objects.all()
    filename = "banned_words.csv"

    with open(filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        
        # Create a list to store the banned words
        banned_word_list = []
        
        for word in banned_words:
            banned_word_list.append(word.word)
        
        # Write all banned words as a single row in the CSV
        csv_writer.writerow(banned_word_list)
