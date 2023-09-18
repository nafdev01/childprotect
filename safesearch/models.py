from django.db import models
from django.utils.text import slugify
from accounts.models import ChildProfile, ParentProfile


class SearchPhrase(models.Model):
    searched_by = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, null=True)
    phrase = models.CharField(max_length=256)
    slug = models.SlugField(max_length=250, null=True, blank=True, editable=False)
    allowed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.phrase)
        super(SearchPhrase, self).save(*args, **kwargs)

    def __str__(self):
        return self.phrase

    class Meta:
        verbose_name = "Search Phrase"
        verbose_name_plural = "Search Phrases"


class BannedWord(models.Model):
    # choices for reasons for a ban
    class BanReason(models.TextChoices):
        INAPPROPRIATE_CONTENT = "IC", "Inappropriate Content"
        OBSCENITIES_AND_PROFANITY = "OP", "Obscenities and Profanity"
        VIOLENT_AND_DISTURBING_CONTENT = "VC", "Violent and Disturbing Content"
        OFFENSIVE_LANGUAGE = "OL", "Offensive Language"

    banned_by = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, null=True)
    word = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=250, null=True, blank=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    reason = models.CharField(
        max_length=2,
        choices=BanReason.choices,
        default=BanReason.INAPPROPRIATE_CONTENT,
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.word)
        super(BannedWord, self).save(*args, **kwargs)

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = "Banned Word"
        verbose_name_plural = "Banned Words"


class FlaggedSearch(models.Model):
    search_phrase = models.ForeignKey(SearchPhrase, on_delete=models.CASCADE, null=True)
    flagged_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.search_phrase

    class Meta:
        verbose_name = "Flagged Search"
        verbose_name_plural = "Flagged Searches "


class FlaggedWord(models.Model):
    search_phrase = models.ForeignKey(SearchPhrase, on_delete=models.CASCADE)
    flagged_word = models.ForeignKey(BannedWord, on_delete=models.CASCADE)

    flagged_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.flagged_word} in {self.search_phrase}"

    class Meta:
        verbose_name = "Flagged Word"
        verbose_name_plural = "Flagged Words"


class FlaggedAlert(models.Model):
    flagged_search = models.ForeignKey(FlaggedSearch, on_delete=models.CASCADE)
    been_reviewed = models.BooleanField(default=False)
    reviewed_on = models.DateTimeField(null=True)
    reviewed_by = models.ForeignKey(ParentProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.flagged_search} flagged for {self.reviewed_by}"

    class Meta:
        verbose_name = "Flagged Alert"
        verbose_name_plural = "Flagged Alerts"
