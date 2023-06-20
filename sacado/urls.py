"""parcours URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import  path, include, re_path
from django.conf.urls.static import static
#import django_cas_ng.views
from setup.views import index

urlpatterns = [
                  path('', include('setup.urls')),
                  path('account/', include('account.urls')),
                  path('group/', include('group.urls')),
                  path('socle/', include('socle.urls')),
                  path('qcm/', include('qcm.urls')),
                  path('sendmail/', include('sendmail.urls')),
                  re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
                  path('school/', include('school.urls')),
                  path('oauth/', include('social_django.urls')),
                  path('basthon/', include('basthon.urls')),    
                  path('association/', include('association.urls')),
                  path('bibliotex/', include('bibliotex.urls')),
                  path('tool/', include('tool.urls')),  
                  path('payment/', include('payment.urls')),
                  path('aefe/', include('aefe.urls')),
                  path('flashcard/', include('flashcard.urls')),
                  path('academy/', include('academy.urls')),
                  path('lesson/', include('lesson.urls')),
                  path('holidaybook/', include('holidaybook.urls')),
                  path('dyshpe/', include('dyshpe.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# handler404 = myapp_views.handler404
# handler500 = myapp_views.handler500


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
