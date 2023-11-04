# safesearch/models,py
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import User


# choices for reasons for a ban
class SearchStatus(models.TextChoices):
    SAFE = "SF", "Safe"
    SUSPICIOUS = "SP", "Suspicious"
    FLAGGED = "FL", "Flagged"


class SearchPhrase(models.Model):
    """Model for Search Instances"""

    class FlaggedSearchManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(search_status=SearchStatus.FLAGGED)

    class SuspiciousSearchManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(search_status=SearchStatus.SUSPICIOUS)

    class SafeSearchManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(search_status=SearchStatus.SAFE)

    searched_by = models.ForeignKey(
        "accounts.ChildProfile", on_delete=models.CASCADE, null=True
    )
    phrase = models.CharField(max_length=256)
    slug = models.SlugField(max_length=250, null=True, blank=True, editable=False)
    search_status = models.CharField(
        max_length=2,
        choices=SearchStatus.choices,
        default=SearchStatus.SAFE,
    )

    objects = models.Manager()
    flagged = FlaggedSearchManager()
    suspicious = SuspiciousSearchManager()
    safe = SafeSearchManager()

    searched_on = models.DateTimeField(auto_now_add=False, default=timezone.now)

    def search_status_counts(parent_profile):
        safe = SearchPhrase.safe.filter(
            searched_by__parent_profile=parent_profile
        ).count()
        suspicious = SearchPhrase.suspicious.filter(
            searched_by__parent_profile=parent_profile
        ).count()
        flagged = SearchPhrase.flagged.filter(
            searched_by__parent_profile=parent_profile,
        ).count()

        search_counts = {
            "safe": safe,
            "suspicious": suspicious,
            "flagged": flagged,
        }
        return search_counts

    def search_status_counts2(child_profile):
        all_searches = SearchPhrase.objects.filter(searched_by=child_profile).count()
        safe = SearchPhrase.safe.filter(searched_by=child_profile).count()
        suspicious = SearchPhrase.suspicious.filter(searched_by=child_profile).count()
        flagged = SearchPhrase.flagged.filter(
            searched_by=child_profile,
        ).count()

        search_counts = {
            "all": all_searches,
            "safe": safe,
            "suspicious": suspicious,
            "flagged": flagged,
        }
        return search_counts

    def flagged_searches(self):
        self.flagged.all()

    @property
    def is_flagged(self):
        if self.search_status == SearchStatus.FLAGGED:
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        self.slug = slugify(self.phrase)
        super(SearchPhrase, self).save(*args, **kwargs)

    def __str__(self):
        return self.phrase

    class Meta:
        verbose_name = "Search Phrase"
        verbose_name_plural = "Search Phrases"
        ordering = ["-searched_on"]


class BanReason(models.TextChoices):
    """Choices for Reasons A Word was Banned"""

    VIOLENT_AND_DISTURBING_CONTENT = "VC", "Violent and Disturbing Content"
    OFFENSIVE_LANGUAGE = "OL", "Offensive Language"
    DRUGS = "DR", "Drugs"
    ADULT_CONTENT = "AC", "Adult Content"


# choices for the type of search
class BannedType(models.TextChoices):
    PHRASE = "P", "Phrase"
    WORD = "W", "Word"


# class for a banned word
class BannedWord(models.Model):
    """Model for Banned Words"""

    class BannedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_banned=True)

    class UnbannedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_banned=False)

    banned_by = models.ForeignKey(
        "accounts.ParentProfile", on_delete=models.CASCADE, null=True
    )
    banned_for = models.ForeignKey(
        "accounts.ChildProfile", on_delete=models.CASCADE, null=True
    )
    word = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, null=True, blank=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    reason = models.CharField(
        max_length=2,
        choices=BanReason.choices,
        default=BanReason.OFFENSIVE_LANGUAGE,
    )
    is_banned = models.BooleanField(default=True)
    banned_type = models.CharField(
        max_length=2,
        choices=BannedType.choices,
        default=BannedType.WORD,
    )
    from_default = models.BooleanField(default=False)

    objects = models.Manager()
    banned = BannedManager()
    unbanned = UnbannedManager()

    def save(self, *args, **kwargs):
        if " " in self.word:
            self.banned_type = BannedType.PHRASE
        else:
            self.banned_type = BannedType.WORD
        self.slug = slugify(self.word)
        self.word = self.word.lower()
        super(BannedWord, self).save(*args, **kwargs)

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = "Banned Word"
        verbose_name_plural = "Banned Words"
        unique_together = ["word", "banned_for"]
        ordering = ["word"]


class FlaggedWord(models.Model):
    """Model for Flagged Word in Flagged Searches"""

    flagged_search = models.ForeignKey(
        SearchPhrase,
        on_delete=models.CASCADE,
        null=True,
        limit_choices_to={"search_status": SearchStatus.FLAGGED},
    )
    flagged_word = models.ForeignKey(BannedWord, on_delete=models.CASCADE)

    flagged_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.flagged_word.word} in {self.flagged_search}"

    class Meta:
        verbose_name = "Flagged Word"
        verbose_name_plural = "Flagged Words"


class SearchAlert(models.Model):
    """Model for Alerts Created during Flagged Searches"""

    class ReviewedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(been_reviewed=True)

    class UnreviewedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(been_reviewed=False)

    flagged_search = models.OneToOneField(
        SearchPhrase,
        on_delete=models.CASCADE,
        limit_choices_to={"search_status": SearchStatus.FLAGGED},
    )
    flagged_on = models.DateTimeField(null=True, editable=False)
    searched_by = models.ForeignKey(
        "accounts.ChildProfile", null=True, editable=False, on_delete=models.CASCADE
    )
    been_reviewed = models.BooleanField(default=False)
    reviewed_on = models.DateTimeField(null=True)
    reviewed_by = models.ForeignKey(
        "accounts.ParentProfile", null=True, editable=False, on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        self.reviewed_by = self.flagged_search.searched_by.parent_profile
        self.searched_by = self.flagged_search.searched_by
        self.flagged_on = self.flagged_search.searched_on
        super(SearchAlert, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.flagged_search} flagged for {self.reviewed_by}"

    class Meta:
        verbose_name = "Flagged Alert"
        verbose_name_plural = "Flagged Alerts"
        ordering = ["been_reviewed", "-flagged_on"]


class UnbanRequest(models.Model):
    """Model for Children Requesting a Banned Word be Unbanned"""

    class ReviewedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(been_reviewed=True)

    class UnreviewedManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(been_reviewed=False)

    banned_word = models.ForeignKey(BannedWord, on_delete=models.CASCADE)
    reason = models.TextField(null=True)
    approved = models.BooleanField(default=False)
    requested_by = models.ForeignKey("accounts.ChildProfile", on_delete=models.CASCADE)
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


class BannedDefault(models.Model):
    """Model for Default Banned Words"""

    word = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, null=True, blank=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    category = models.CharField(
        max_length=2,
        choices=BanReason.choices,
        default=BanReason.OFFENSIVE_LANGUAGE,
    )
    banned_type = models.CharField(
        max_length=2,
        choices=BannedType.choices,
        default=BannedType.WORD,
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.word)
        self.word = self.word.lower()
        super(BannedDefault, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Banned Default"
        verbose_name_plural = "Banned Defaults"
        unique_together = ["word", "category"]

    def __str__(self):
        return f"default banned word: {self.word}"


class ResultReport(models.Model):
    """Model for Child Reporting Results to Parents"""

    child = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        null=True,
        limit_choices_to={"user_type": User.UserType.CHILD},
    )
    search = models.ForeignKey(
        SearchPhrase,
        on_delete=models.CASCADE,
        null=True,
    )
    result_title = models.CharField(max_length=250)
    result_link = models.URLField(max_length=250)
    result_snippet = models.TextField()
    report_reason = models.TextField()
    reported_on = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.result_title} reported by {self.child}"

    class Meta:
        verbose_name = "Result Report"
        verbose_name_plural = "Result Reports"
        ordering = ["-reported_on"]


class SiteVisit(models.Model):
    """Model for Site Visits"""

    child = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        null=True,
        limit_choices_to={"user_type": User.UserType.CHILD},
    )
    search = models.ForeignKey(
        SearchPhrase,
        on_delete=models.CASCADE,
        null=True,
    )

    site_link = models.URLField(max_length=250)
    site_title = models.CharField(max_length=250)
    site_snippet = models.TextField()
    visited_on = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.site_link} visited by {self.child}"

    class Meta:
        verbose_name = "Site Visite"
        verbose_name_plural = "Site Visites"
        ordering = ["-visited_on"]
