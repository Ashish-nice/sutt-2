from django.contrib import admin
from .models import Book, Borrow

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'copies_total', 'copies_available')
    search_fields = ('title', 'author', 'isbn')

@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrowed_date', 'returned_date', 'late_fees')
    list_filter = ('borrowed_date', 'returned_date')
    search_fields = ('user__username', 'book__title')
