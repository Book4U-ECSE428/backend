from django.db import models

"""
one - one: models.OneToOneField(
        CLASS,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    in either
many - many: models.ManyToManyField in either
one - many: foreignkey in many
"""
GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
    ("Unknown", "Unknown")
)

PERMISSION_CHOICES = (
    ("normal", 'normal'),
    ("banned", 'banned'),
    ("moderator", 'moderator'),
)


class User(models.Model):
    name = models.CharField(max_length=100, default="")
    password = models.CharField(max_length=100, default="")
    e_mail = models.CharField(max_length=100, default="")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="Unknown")
    personal_intro = models.CharField(max_length=1000, default="")
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default="normal")

    def __str__(self):
        return self.name + '' + self.e_mail


class BookCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    summary = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Book(models.Model):
    ISBN = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    publish_date = models.DateField()
    publish_firm = models.CharField(max_length=100)
    edition = models.CharField(max_length=100)
    visibility = models.BooleanField(default=False)
    category = models.ManyToManyField(BookCategory)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    cover_image = models.TextField()

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=9999)
    rating = models.IntegerField()
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    liked_counter = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user.name)


class Vote(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        primary_key=False,
    )
    count = models.IntegerField(default=0)
    review = models.ForeignKey(
        Review,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return "vote by: " + self.user.name


class Comment(models.Model):
    index = models.IntegerField()
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=9999, default='')
    modified = models.BooleanField(default=False)
    report_counter = models.IntegerField(default=0)

    def __str__(self):
        return "comment by: " + self.user.name
