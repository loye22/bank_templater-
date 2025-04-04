# # """
# # URL configuration for bank_templater project.

# # The `urlpatterns` list routes URLs to views. For more information please see:
# #     https://docs.djangoproject.com/en/5.1/topics/http/urls/
# # Examples:
# # Function views
# #     1. Add an import:  from my_app import views
# #     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# # Class-based views
# #     1. Add an import:  from other_app.views import Home
# #     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# # Including another URLconf
# #     1. Import the include() function: from django.urls import include, path
# #     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# # """
# # from django.contrib import admin
# # from django.urls import path
# # from myapp import views

# # urlpatterns = [
# #     path('admin/', admin.site.urls),
# #     path('import/', views.import_json, name='import_json'),
# #     path('get_daily_summaries/', views.get_daily_summaries, name='get_daily_summaries'),
# #     path('get_transactions/', views.get_transactions, name='get_transactions'), 
# # ]


from myapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin 
from django.urls import path
from myapp import views  # Correctly import views from the myapp application

urlpatterns = [
    path('', views.import_json, name='import_json'),
    path('admin/', admin.site.urls),
    path('processed-files/', views.processed_files, name='processed_files'),
    path('get_daily_summaries/', views.get_daily_summaries, name='get_daily_summaries'),
    path('get_transactions/', views.get_transactions, name='get_transactions'),  # Add this line
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
