import datetime

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from .forms import RenewBookForm, RenewBookModelForm
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
@login_required
def detail_book(request, pk):
    try:
        book = Book.objects.get(pk=pk)
        return render(request, "books/detail.html", {"book": book})
    except Book.DoesNotExist as ex:
        return render(request, "404.html", {"errors": ex})


class AuthorListView(generic.ListView):
    model = Author
    template_name = "authors/index.html"
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author

    template_name = "authors/detail.html"


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = "bookinstances/list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


class LoanedBookListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = "bookinstances/list_borrowed.html"
    paginate_by = 10
    queryset = BookInstance.objects.filter(status__exact="o").order_by("due_back")


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == "POST":
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()

            return HttpResponseRedirect(reverse("list-book-borrowed"))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})
        # form = RenewBookModelForm(initial={"due_date": proposed_renewal_date})

    context = {"form": form, "book_instance": book_instance}

    return render(request, "bookinstances/book_renew_librarian.html", context)


class AuthorCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    initial = {"date_of_death": "11/06/2020"}
    template_name = "authors/new.html"
    permission_required = "catalog.can_mark_returned"


class AuthorUpdate(UpdateView):
    model = Author
    fields = "__all__"
    template_name = "authors/new.html"


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy("authors")
    template_name = "authors/confirm_delete.html"


# def handle_not_found(request, exception):
#     return render(request, "404.html", {"errors": exception})
