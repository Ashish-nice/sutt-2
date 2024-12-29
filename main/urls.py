from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('books/borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('books/return/<int:borrow_id>/', views.return_book, name='return_book'),
    path('my-borrowed-books/', views.borrowed_books, name='borrowed_books'),
    path('history/', views.history, name='history'),
]