# Engage_Peo/urls.py
from django.contrib import admin
from django.urls import path
from engage_chat.views import chat_page, services_query

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', chat_page),         # UI
    path('ask/', services_query) # API
]
