from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.StoryView.as_view(), name="story"),
    path('add-story/', login_required(views.AddStoryView.as_view()), name='newStory'),
    path('<int:pk>/edit/', views.StoryEditView.as_view(), name='storyEdit'),
    path('<int:pk>/delete/', views.DeleteView.as_view(), name='deleteStory'),
    path('<int:pk>/like/', views.like, name='like'),
]
