from django.urls import path
from . import views
from .views import ProductUpdateView, ProductDeleteView, ProductListView


urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('order/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path("manage-users/", views.manage_users, name="manage_users"),
    path("delete-user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("promote-user/<int:user_id>/", views.promote_to_admin, name="promote_user"),    
    path('product/edit/<int:pk>/', ProductUpdateView.as_view(), name='edit_product'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='delete_product'),
    path('manage-users/promote/<int:user_id>/<str:role>/', views.promote_user, name='promote_user'),
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:review_id>/reply/', views.reply_to_review, name='reply_to_review'),
    path("orders/<int:order_id>/ship/", views.mark_order_shipped, name="mark_order_shipped"),



]
