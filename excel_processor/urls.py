from django.urls import path
from . import views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('merge-data/', views.merge_data, name='merge_data'),
    path('save-changes/', views.save_changes, name='save_changes'),
    path('download_output/', views.download_output, name='download_output'),

]

