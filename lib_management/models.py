from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Book Model
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    category = models.ForeignKey(
        Category, related_name="books", on_delete=models.SET_NULL,
        null=True, blank=True
    )
    shelf = models.IntegerField(null=True, blank=True)
    row = models.IntegerField(null=True, blank=True)
    column = models.IntegerField(null=True, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover = models.ImageField(
        upload_to="covers/", null=True, blank=True, default="covers/default.png"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"
    

# Signal
@receiver(pre_save, sender=Book)
def update_available_copies(sender, instance, **kwargs):
    if not instance.pk:
        instance.available_copies = instance.total_copies
        return

    try:
        original = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if original.total_copies != instance.total_copies:
        diff = instance.total_copies - original.total_copies
        
        if diff > 0:
            instance.available_copies += diff
        
        elif diff < 0:
            if instance.available_copies > instance.total_copies:
                instance.available_copies = instance.total_copies


# Borrower Model
class Borrower(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=11, blank=True, null=True) 
    email = models.EmailField(blank=True, null=True)   
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


# Borrowing Model
class Borrowing(models.Model):
    book = models.ForeignKey(Book, related_name="borrowings", on_delete=models.CASCADE)
    borrower = models.ForeignKey(Borrower, related_name="borrowings", on_delete=models.CASCADE)
    date_borrowed = models.DateTimeField(default=timezone.now)
    date_due = models.DateTimeField(null=True, blank=True)
    date_returned = models.DateTimeField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_date_returned = self.date_returned

    def save(self, *args, **kwargs):
        is_new_borrowing = not self.pk
        is_returning = self.pk and self.date_returned and not self.__original_date_returned

        # Borrowing Logic
        if is_new_borrowing:
            self.date_due = timezone.now() + timedelta(days=7)
            if self.book.available_copies > 0:
                self.book.available_copies -= 1
                self.book.save(update_fields=['available_copies'])
                
            super().save(*args, **kwargs)

        elif is_returning:
            if self.date_due and self.date_returned > self.date_due:
                
                date_due_only = self.date_due.date()
                date_returned_only = self.date_returned.date()

                time_difference = date_returned_only - date_due_only
                
                if time_difference.days > 0:
                    days_late = time_difference.days
                    self.fine_amount = days_late * 30 
                else:
                    self.fine_amount = 0
            
            else:
                self.fine_amount = 0 

            self.book.available_copies += 1
            if self.book.available_copies > self.book.total_copies:
                 self.book.available_copies = self.book.total_copies
                 
            self.book.save(update_fields=['available_copies'])
            super().save(update_fields=['date_returned', 'fine_amount'], *args, **kwargs)

        else:
            super().save(*args, **kwargs)