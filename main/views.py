from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Book, Borrow
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from datetime import timedelta, date

# Create your views here.
@login_required
def home(request):
    books = Book.objects.all()  # Get all books
    query = request.GET.get('q')  # Search query
    if query:
        books = books.filter(title__icontains=query)  # Filter by title containing query

    book_count = books.count()  # Total books count

    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page')  # Current page number
    page_obj = paginator.get_page(page_number)  # Get page object

    borrowed_books = Borrow.objects.filter(user=request.user, returned_date__isnull=True).values_list('book_id', flat=True)

    return render(request, 'main/home.html', {
        'page_obj': page_obj,
        'book_count': book_count,
        'query': query,
        'books': books,  # Add books to context
        'borrowed_books': borrowed_books,  # Add borrowed books to context
    })

def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if user is not authenticated

    existing_borrow = Borrow.objects.filter(user=request.user, book=book, returned_date__isnull=True).exists()

    if existing_borrow:
        return render(request, 'main/borrow_error.html', {'message': 'You have already borrowed this book.'})

    if book.copies_available > 0:
        Borrow.objects.create(
            user=request.user,
            book=book,
            due_date=date.today() + timedelta(days=14)  # 14 days issue period
        )
        book.copies_available -= 1
        book.save()
        return render(request, 'main/borrow_success.html', {'book_title': book.title})  # Pass book title to success template
    else:
        return render(request, 'main/borrow_error.html', {'message': 'No copies available'})
    
def return_book(request, borrow_id):
    borrow = get_object_or_404(Borrow, id=borrow_id)
    borrow.returned_date = date.today()

    # Calculate late fees if applicable
    if borrow.returned_date > borrow.due_date:
        late_days = (borrow.returned_date - borrow.due_date).days
        borrow.late_fees = late_days * 5  # Assume 5 units per day as late fee

    borrow.save()

    # Update book availability
    book = borrow.book
    book.copies_available += 1
    book.save()

    return render(request, 'main/return_success.html')  # Update to the correct path

def borrowed_books(request):
    borrows = Borrow.objects.filter(user=request.user, returned_date__isnull=True)
    return render(request, 'main/borrowed_books.html', {'borrows': borrows})

@login_required
def history(request):
    borrows = Borrow.objects.filter(user=request.user, returned_date__isnull=False).order_by('-returned_date')
    return render(request, 'main/history.html', {'borrows': borrows})
