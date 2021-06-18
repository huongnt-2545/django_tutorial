from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
from datetime import date

# Create your models here.


class Author(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_death = models.DateField("died", null=True, blank=True)

    def __str__(self):
        return f"{self.first_name}, {self.last_name}"

    def get_absolute_url(self):
        return reverse("author-detail", args=[str(self.id)])

    class Meta:
        ordering = ["first_name", "last_name"]


class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="Enter a book genre")

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100, help_text="Enter a language")

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200, help_text="Enter field title")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book"
    )
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=True,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>',
    )
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    language = models.ManyToManyField(
        Language, help_text="Select a language for this book"
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book-detail", args=[str(self.id)])

    def display_genre(self):
        return ", ".join(genre.name for genre in self.genre.all()[:3])

    def display_language(self):
        return ", ".join(language.name for language in self.language.all())

    display_genre.short_description = "Genre"
    display_language.short_description = "Language"


class BookInstance(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, help_text="Unique ID for particular book"
    )
    due_back = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)

    LOAN_STATUS = (
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reserved"),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="m",
        help_text="Book availability",
    )
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        return self.due_back and date.today() > self.due_back

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        return f"{self.id} ({self.book.title})"
