from django.db import models

class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('ต้ม', 'ต้ม'),
        ('ผัด', 'ผัด'),
        ('ทอด', 'ทอด'),
        ('ของหวาน', 'ของหวาน'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    ingredients = models.TextField()
    instructions = models.TextField()

    def __str__(self):
        return self.name
