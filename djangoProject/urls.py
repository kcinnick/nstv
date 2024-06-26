"""nstv_fe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from nstv import views

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.index),
    path('shows_index', views.shows_index, name='shows_index'),
    path('shows/<int:show_id>', views.show_index, name='show_index'),
    path('shows/<int:show_id>/episode/<int:episode_id>/download', views.download_episode, name='download_episode'),
    path('movies_index', views.movies_index, name='movies_index'),
    path('add_show', views.add_show_page, name='add_show'),
    path('add_movie', views.add_movie_page, name='add_movie'),
    path('delete/movies/<int:movie_id>', views.delete_movie, name='delete_movie'),
    path('delete/<int:show_id>', views.delete_show, name='delete_show'),
    path('delete/<int:show_id>/episode/<int:episode_id>', views.delete_episode_of_show, name='delete_episode_of_show'),
    path('delete/movie/<int:movie_id>', views.delete_movie, name='delete_movie'),
    path('shows/<int:show_id>/add_episodes_to_database', views.add_episodes_to_database,
         name='add_episodes_to_database'),
    path('movies/<int:movie_id>/download', views.download_movie, name='download_movie'),
    path('shows/move_downloaded_files_to_plex', views.move_downloaded_tv_show_files_to_plex, name='move_downloaded_tv_show_files_to_plex'),
    path('movies/move_downloaded_files_to_plex', views.move_downloaded_movie_files_to_plex, name='move_downloaded_movie_files_to_plex'),
    path('movies/<int:movie_id>', views.movie_index, name='movie_index'),
    path('cast/<int:cast_member_id>', views.cast_member, name='cast_member_index'),
    path('search/', views.search_results, name='search_results'),
    path('shows/<int:show_id>/missing_episodes', views.find_missing_episodes, name='missing_episodes'),
]