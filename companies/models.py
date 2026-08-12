from django.db import models


class WatchedCompany(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True)
    sector = models.CharField(max_length=100, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]
        verbose_name = "Obserwowana spółka"
        verbose_name_plural = "Obserwowane spółki"

    def __str__(self):
        return f"{self.ticker} — {self.name}"
