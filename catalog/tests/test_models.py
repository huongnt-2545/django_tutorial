from django.test import TestCase

from catalog.models import Author


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name="An", last_name="dy")

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_author = author._meta.get_field("first_name").verbose_name
        self.assertEqual(field_author, "first name")

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_author = author._meta.get_field("date_of_death").verbose_name
        self.assertEqual(field_author, "died")

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field("first_name").max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f"{author.first_name}, {author.last_name}"
        self.assertEqual(str(author), expected_object_name)

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(author.get_absolute_url(), "/catalog/authors/1")
