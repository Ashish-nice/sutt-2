from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView
from .models import Book, Borrow
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from datetime import timedelta, date
import pandas as pd
from .forms import UploadExcelForm

class HomeView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'main/home.html'
    context_object_name = 'books'  # Changed from page_obj to books
    paginate_by = 10

    def get_queryset(self):
        queryset = Book.objects.all().order_by('title')  # Added ordering
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(title__icontains=query)  # Changed back to title
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = self.get_queryset()
        context['book_count'] = books.count()
        context['query'] = self.request.GET.get('q')
        context['page_obj'] = context['page_obj']  # Keep page_obj for pagination
        context['borrowed_books'] = Borrow.objects.filter(
            user=self.request.user, 
            returned_date__isnull=True
        ).values_list('book_id', flat=True)
        return context

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    existing_borrow = Borrow.objects.filter(
        user=request.user, 
        book=book, 
        returned_date__isnull=True
    ).exists()

    if existing_borrow:
        messages.error(request, 'You have already borrowed this book.')
        return redirect('home')

    if book.copies_available > 0:
        Borrow.objects.create(
            user=request.user,
            book=book,
            due_date=date.today() + timedelta(days=14)
        )
        book.copies_available -= 1
        book.save()
        messages.success(request, f'Successfully borrowed "{book.title}".')
    else:
        messages.error(request, 'No copies available.')
    
    return redirect('home')

@login_required
def return_book(request, borrow_id):
    borrow = get_object_or_404(Borrow, id=borrow_id)
    borrow.returned_date = date.today()

    if borrow.returned_date > borrow.borrowed_date+timedelta(days=20):
        late_days = (borrow.returned_date - borrow.due_date).days
        borrow.late_fees = late_days * 5
        messages.warning(request, f'Book returned with {late_days} days late. Late fee: {borrow.late_fees} units.')
    else:
        messages.success(request, f'Successfully returned "{borrow.book.title}".')

    borrow.save()
    book = borrow.book
    book.copies_available += 1
    book.save()

    return redirect('home')

class HistoryView(LoginRequiredMixin, ListView):
    model = Borrow
    template_name = 'main/history.html'
    context_object_name = 'borrows'

    def get_queryset(self):
        return Borrow.objects.filter(
            user=self.request.user, 
            returned_date__isnull=False
        ).order_by('-returned_date')
    
@login_required
def upload_books(request):
    try:
        if not hasattr(request.user, 'user_type') or request.user.user_type != 'librarian':
            messages.error(request, "You do not have permission to perform this action.")
            return redirect('home')

        if request.method == 'POST':
            form = UploadExcelForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # Changed 'file' to 'excel_file' to match form field name
                    excel_file = request.FILES['excel_file']
                    df = pd.read_excel(excel_file)

                    # Ensure the required columns exist
                    required_columns = ['title', 'author', 'publisher', 'isbn', 'copies_total', 'copies_available']
                    if not all(col in df.columns for col in required_columns):
                        messages.error(request, "Invalid file format. Ensure all required columns are present.")
                        return redirect('upload_books')

                    # Add books to the database
                    for _, row in df.iterrows():
                        Book.objects.update_or_create(
                            isbn=row['isbn'],  # Unique field for identification
                            defaults={
                                'title': row['title'],
                                'author': row['author'],
                                'publisher': row['publisher'],
                                'copies_total': row['copies_total'],
                                'copies_available': row['copies_available'],
                            }
                        )

                    messages.success(request, "Books have been successfully uploaded.")
                    return redirect('home')

                except Exception as e:
                    messages.error(request, f"An error occurred: {str(e)}")
                    return redirect('upload_books')
        else:
            form = UploadExcelForm()

        return render(request, 'main/upload_books.html', {'form': form})  # Add main/ prefix
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')