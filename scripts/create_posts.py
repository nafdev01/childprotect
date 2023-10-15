import csv
from safesearch.models import FlaggedAlert
from faker import Faker
from forum.models import Post

no_of_posts = int(input("How may posts to create: "))

fake = Faker()


def run():
    for i in range(0, no_of_posts):
        title = fake.sentence()
        content = fake.paragraph(10)
        posted_on = fake.date_time_between(start_date="-30d", end_date="now")
        updated_on = fake.date_time_between(start_date=posted_on, end_date="now")

        post = Post.objects.create(
            title=title, content=content, posted_on=posted_on, updated_on=updated_on
        )
        post.save()
