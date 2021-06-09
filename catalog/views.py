from django.shortcuts import render
from django.views import generic

from .models import Book, BookInstance, Author, Genre

# Create your views here.
def index(request):
    #
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Book instances available
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()
    num_genres = Genre.objects.filter(name__contains="n").count()
    num_authors = Author.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_genres": num_genres,
        "num_visits": num_visits,
    }

    return render(request, "index.html", context)


class BookListView(generic.ListView):
    model = Book

    context_object_name = "list_books"  # if not desc, default name is book_list
    queryset = Book.objects.all()[:10]  # default query all
    template_name = "books/index.html"  # default: /templates/catalog/book_list.html
    paginate_by = 1


# class BookDetailView(generic.DetailView):
#     model = Book

#     template_name = "books/detail.html"  # default: /templates/catalog/book_detail.html
def detail_book(request, pk):
    try:
        book = Book.objects.get(pk=pk)
        return render(request, "books/detail.html", {"book": book})
    except Book.DoesNotExist as ex:
        return render(request, "404.html", {"errors": ex})


class AuthorListView(generic.ListView):
    model = Author
    template_name = "authors/index.html"


class AuthorDetailView(generic.DetailView):
    model = Author

    template_name = "authors/detail.html"


# def handle_not_found(request, exception):
#     return render(request, "404.html", {"errors": exception})
