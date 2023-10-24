# safesearch/models,py
from django.db import models
from django.utils.text import slugify
from accounts.models import ChildProfile, ParentProfile
from django.utils import timezone


# choices for reasons for a ban
class SearchStatus(models.TextChoices):
    SAFE = "SF", "Safe"
    SUSPICIOUS = "SP", "Suspicious"
    FLAGGED = "FL", "Flagged"


class SearchPhrase(models.Model):
    searched_by = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, null=True)
    phrase = models.CharField(max_length=256)
    slug = models.SlugField(max_length=250, null=True, blank=True, editable=False)
    search_status = models.CharField(
        max_length=2,
        choices=SearchStatus.choices,
        default=SearchStatus.SAFE,
    )

    searched_on = models.DateTimeField(auto_now_add=False, default=timezone.now)

    def search_status_counts(parent_profile):
        safe = SearchPhrase.objects.filter(
            searched_by__parent_profile=parent_profile, search_status=SearchStatus.SAFE
        ).count()
        suspicious = SearchPhrase.objects.filter(
            searched_by__parent_profile=parent_profile,
            search_status=SearchStatus.SUSPICIOUS,
        ).count()
        flagged = SearchPhrase.objects.filter(
            searched_by__parent_profile=parent_profile,
            search_status=SearchStatus.FLAGGED,
        ).count()

        search_counts = {
            "safe": safe,
            "suspicious": suspicious,
            "flagged": flagged,
        }
        return search_counts

    def save(self, *args, **kwargs):
        self.slug = slugify(self.phrase)
        super(SearchPhrase, self).save(*args, **kwargs)

    def __str__(self):
        return self.phrase

    class Meta:
        verbose_name = "Search Phrase"
        verbose_name_plural = "Search Phrases"
        ordering = ["searched_on"]


# choices for reasons for a ban
class BanReason(models.TextChoices):
    INAPPROPRIATE_CONTENT = "IC", "Inappropriate Content"
    OBSCENITIES_AND_PROFANITY = "OP", "Obscenities and Profanity"
    VIOLENT_AND_DISTURBING_CONTENT = "VC", "Violent and Disturbing Content"
    OFFENSIVE_LANGUAGE = "OL", "Offensive Language"


# class for a banned word
class BannedWord(models.Model):
    class BannedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_banned=True)

    class UnbannedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_banned=False)

    banned_by = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, null=True)
    word = models.CharField(max_length=50)
    slug = models.SlugField(max_length=250, null=True, blank=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    reason = models.CharField(
        max_length=2,
        choices=BanReason.choices,
        default=BanReason.INAPPROPRIATE_CONTENT,
    )
    is_banned = models.BooleanField(default=True)

    objects = models.Manager()
    banned = BannedManager()
    unbanned = UnbannedManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.word)
        self.word = self.word.lower()
        super(BannedWord, self).save(*args, **kwargs)

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = "Banned Word"
        verbose_name_plural = "Banned Words"
        unique_together = ["word", "banned_by"]
        ordering = ["word"]


class FlaggedSearch(models.Model):
    search_phrase = models.OneToOneField(
        SearchPhrase, on_delete=models.CASCADE, null=True
    )
    flagged_on = models.DateTimeField(auto_now_add=True)
    searched_by = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        self.searched_by = self.search_phrase.searched_by
        super(FlaggedSearch, self).save(*args, **kwargs)

    @property
    def flagged_words(self):
        words = self.flaggedword_set.all()
        return words

    def __str__(self):
        return self.search_phrase.phrase

    class Meta:
        verbose_name = "Flagged Search"
        verbose_name_plural = "Flagged Searches "


class FlaggedWord(models.Model):
    flagged_search = models.ForeignKey(
        FlaggedSearch, on_delete=models.CASCADE, null=True
    )
    flagged_word = models.ForeignKey(BannedWord, on_delete=models.CASCADE)

    flagged_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.flagged_word.word} in {self.flagged_search}"

    class Meta:
        verbose_name = "Flagged Word"
        verbose_name_plural = "Flagged Words"


class FlaggedAlert(models.Model):
    class ReviewedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(been_reviewed=True)

    class UnreviewedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(been_reviewed=False)

    flagged_search = models.OneToOneField(FlaggedSearch, on_delete=models.CASCADE)
    flagged_on = models.DateTimeField(null=True, editable=False)
    searched_by = models.ForeignKey(
        ChildProfile, null=True, editable=False, on_delete=models.CASCADE
    )
    been_reviewed = models.BooleanField(default=False)
    reviewed_on = models.DateTimeField(null=True)
    reviewed_by = models.ForeignKey(
        ParentProfile, null=True, editable=False, on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        self.reviewed_by = self.flagged_search.search_phrase.searched_by.parent_profile
        self.searched_by = self.flagged_search.search_phrase.searched_by
        self.flagged_on = self.flagged_search.flagged_on
        super(FlaggedAlert, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.flagged_search} flagged for {self.reviewed_by}"

    class Meta:
        verbose_name = "Flagged Alert"
        verbose_name_plural = "Flagged Alerts"
        ordering = ["been_reviewed", "-flagged_on"]


class UnbanRequest(models.Model):
    class ReviewedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(been_reviewed=True)

    class UnreviewedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(been_reviewed=False)

    banned_word = models.ForeignKey(BannedWord, on_delete=models.CASCADE)
    reason = models.TextField(null=True)
    approved = models.BooleanField(default=False)
    requested_by = models.ForeignKey(ChildProfile, on_delete=models.CASCADE)
    requested_on = models.DateTimeField(auto_now_add=True)
    been_reviewed = models.BooleanField(default=False)
    reviewed_on = models.DateTimeField(null=True)
    seen_by_child = models.BooleanField(default=False)
    seen_on = models.DateTimeField(null=True)

    objects = models.Manager()
    reviewed = ReviewedManager()
    unreviewed = UnreviewedManager()

    def __str__(self):
        return f"{self.banned_word} unban request"

    class Meta:
        verbose_name = "Unban Request"
        verbose_name_plural = "Unban Requests"
        unique_together = ["banned_word", "requested_by"]
        ordering = ["-requested_on"]


class SuspiciousSearch(models.Model):
    search_phrase = models.ForeignKey(SearchPhrase, on_delete=models.CASCADE)
    flagged_results = models.PositiveIntegerField(editable=False)
    been_reviewed = models.BooleanField(default=False)
    reviewed_on = models.DateTimeField(null=True)
    seen_by_child = models.BooleanField(default=False)
    seen_on = models.DateTimeField(null=True)

    def __str__(self):
        return f"Suspicious search {self.search_phrase}"

    class Meta:
        verbose_name = "Suspicious Search"
        verbose_name_plural = "Suspicious Searches"
