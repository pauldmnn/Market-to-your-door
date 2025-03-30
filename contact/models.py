from django.db import models


class CustomerQuestion(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"
