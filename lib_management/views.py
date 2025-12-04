from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from .models import Book, Category, Borrower, Borrowing
from .serializers import (
    BookSerializer, 
    CategorySerializer, 
    BorrowerSerializer, 
    BorrowingSerializer
)


# API ViewSets
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'author', 'category__name']
    permission_classes = [IsAuthenticated]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class BorrowerViewSet(viewsets.ModelViewSet):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer
    permission_classes = [IsAuthenticated]

class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().order_by('-id')
    # --- CRITICAL FIX 2: Using the correct Serializer ---
    serializer_class = BorrowingSerializer 
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check availability before creation (Good defensive coding)
        book_id = request.data.get('book_id')
        try:
            book = Book.objects.get(pk=book_id)
            if book.available_copies <= 0:
                return Response({'error': 'No copies available for borrowing.'}, 
                                status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({'book_id': 'Book not found.'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # The Borrowing model's save() method handles decrementing inventory.
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


# Frontend Rendering Views
def index(request):
    return render(request, 'index.html')

def books(request):
    return render(request, 'books.html')

def add_book(request):
    return render(request, 'add-book.html')
    
def borrowed(request):
    return render(request, 'borrowed.html')

def borrow_book(request):
    return render(request, 'borrow-book.html')

def homepage(request):
    return render(request, 'homepage.html')

