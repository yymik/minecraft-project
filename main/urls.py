from django.urls import path
from .views import home_view

<<<<<<< HEAD
=======
app_name = 'main'

>>>>>>> 1756a89 (0608 15:51 json 스킨편집기)
urlpatterns = [
    path('', home_view, name='home'),
]
