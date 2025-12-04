from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('books/', views.books, name='books'), 
    path('add-book/', views.add_book, name='add_book'), 
    path('borrowed/', views.borrowed, name='borrowed'),
    path('borrow-book/', views.borrow_book, name='borrow_book'),
    path('homepage/', views.homepage, name='homepage'), 
]