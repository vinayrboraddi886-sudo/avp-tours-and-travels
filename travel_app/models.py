from django.db import models

class Destination(models.Model):
    destination_name = models.CharField(max_length=100)
    country          = models.CharField(max_length=100, blank=True)
    description      = models.TextField(blank=True)
    price_inr        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_usd        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    best_time        = models.CharField(max_length=100, blank=True)
    duration_days    = models.IntegerField(default=5)
    category         = models.CharField(max_length=50, blank=True)
    image_url        = models.TextField(blank=True)
    is_active        = models.BooleanField(default=True)
    class Meta:
        db_table = 'destinations'

class Package(models.Model):
    destination   = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True)
    package_name  = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    price_inr     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_usd     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_days = models.IntegerField(default=5)
    includes      = models.TextField(blank=True)
    image_url     = models.TextField(blank=True)
    is_active     = models.BooleanField(default=True)
    class Meta:
        db_table = 'packages'

class Booking(models.Model):
    full_name        = models.CharField(max_length=100)
    email            = models.EmailField()
    phone            = models.CharField(max_length=20, blank=True)
    destination      = models.CharField(max_length=100)
    travel_date      = models.DateField()
    people           = models.IntegerField(default=1)
    budget_inr       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_usd       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_requests = models.TextField(blank=True)
    status           = models.CharField(max_length=20, default='pending')
    created_at       = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'bookings'

class Review(models.Model):
    name        = models.CharField(max_length=100)
    email       = models.EmailField(blank=True)
    destination = models.CharField(max_length=100, blank=True)
    rating      = models.IntegerField(default=5)
    review_text = models.TextField()
    approved    = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'reviews'

class User(models.Model):
    name       = models.CharField(max_length=100)
    email      = models.EmailField(unique=True)
    phone      = models.CharField(max_length=20, blank=True)
    password   = models.CharField(max_length=255)
    role       = models.CharField(max_length=10, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'users'