from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'borrowers', views.BorrowerViewSet)
router.register(r'borrowings', views.BorrowingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]