from django.db import models
from django.conf import settings
from datetime import timedelta
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    copies_total = models.IntegerField(default=1)
    copies_available = models.IntegerField(default=1)
    cover_image = models.ImageField(default='book_covers/default_cover.jpg', upload_to='book_covers/', blank=True, null=True)

    def __str__(self):
        return self.title

class Borrow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(editable=False)
    returned_date = models.DateField(null=True, blank=True)
    late_fees = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.borrowed_date + timedelta(days=20)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
