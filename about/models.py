from django.db import models


class AboutUs(models.Model):
    title = models.CharField(max_length=200, default="About Us")
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "About Page Content"



