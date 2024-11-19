from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # View
    path('', views.viewhome,name='viewhome'),
 

    # Main
    path('home/',views.home,name='home'),
    path('mypost/',views.mypost,name='mypost'),
    path('postpage/',views.postpage,name='postpage'),
    path('savelike/',views.savelike,name='savelike'),
    path('search/', views.search, name='search'),


    # FILTER
    path('top-rating/', views.rating_recipes, name='rating_recipes'),
    path('top-view/', views.view_recipes, name='view_recipes'),
    

    # login-out
    path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutPage,name='logout'),
    path('register/',views.register,name='register'),
    

     # Các URL khác
    path('recipe/delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
    path('like/<int:recipe_id>/', views.like_recipe, name='like_recipe'),
    path('unlike/<int:recipe_id>/', views.unlike_recipe, name='unlike_recipe'),  # Xóa yêu thích
    path('detail/<int:recipe_id>/',views.detail,name='detail'), #Xem Chi Tiet Từng SP
    path('recipe/<int:recipe_id>/rate/', views.rate_recipe, name='rate_recipe'),
    path('recipe/<int:recipe_id>/reset_rating/',views.reset_rating, name='reset_rating'),
    path('recipe/edit/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'), 



    path('recipes/<str:classify>/', views.recipes_by_classify, name='recipes_by_classify'),



    # ADMIN
    path('ad/', views.admin_app, name='ad'), # Đường dẫn đến trang admin
    path('delete-admin/<int:post_id>/', views.admin_delete, name='admin_delete'),
    path('edit-admin/<int:recipe_id>/', views.admin_edit, name='admin_edit'),
    path('addetail/<int:recipe_id>/',views.addetail,name='addetail'),
    path('ad/delete/<int:recipe_id>/', views.admin_myrecipe, name='admin_myrecipe'),
    
    path('addetail/delete/<int:comment_id>/', views.addelete_comment, name='addelete_comment'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    path('users/', views.users, name='users'),
    # URL để tìm kiếm người dùng
    path('search/', views.search_user, name='search_user'),
    # URL để xóa người dùng
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]