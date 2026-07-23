from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('about/', views.about_view, name='about'),

    path('pets/', views.pet_list, name='pet_list'), # صفحة كل الحيوانات
    path('pets/<str:species>/', views.pet_list_by_species, name='pet_list_by_species'), 

    path('dashboard/', views.dashboard_view, name='dashboard'),    path('dashboard/request/<int:request_id>/<str:action>/', views.update_request_status, name='update_request_status'),
    path('dashboard/my-pets/', views.my_pets_view, name='my_pets'),
    path('dashboard/pet/delete/<int:pet_id>/', views.delete_pet_view, name='delete_pet'),
    # path('dashboard/pet/edit/<int:pet_id>/', views.edit_pet_view, name='edit_pet'),

    path('browse-pets/', views.browse_pets_view, name='browse_pets'),

    path('pet/<int:pet_id>/', views.pet_detail_view, name='pet_detail'),

    path('pet/<int:pet_id>/adopt/', views.adopt_pet_view, name='adopt_pet'),
    path('my-requests/', views.my_requests_view, name='my_requests'),

]
    