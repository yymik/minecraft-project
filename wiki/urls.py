from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    path('', views.wiki_main, name='wiki_main'),
    path('all-pages/', views.wiki_all_pages, name='all_pages'),
    path('search/', views.wiki_search, name='wiki_search'),
    path('recent-changes/', views.recent_changes, name='recent_changes'),
    path('discussions/', views.recent_discussions, name='recent_discussions'),
    path('discussions/new/', views.discussion_new, name='discussion_new'),
    path('discussions/<str:topic_id>/', views.discussion_detail, name='discussion_detail'),
    path('contact/', views.contact_view, name='contact'),
    path('recruit/', views.recruit_view, name='recruit'),
    path('qa/', views.qa_list, name='qa_list'),
    path('qa/new/', views.qa_new, name='qa_new'),
    path('qa/<str:qid>/', views.qa_detail, name='qa_detail'),
    path('category/<slug:category_slug>/', views.wiki_category_overview, name='wiki_category'),
    path('<path:title>/partial/', views.wiki_detail_partial, name='wiki_detail_partial'),
    path('<path:title>/edit/', views.wiki_edit_view, name='wiki_edit'),
    path('<path:title>/', views.wiki_detail_view, name='wiki_detail'),
]
