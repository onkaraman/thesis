from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from user_profile import views as user_profile_views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^signup/$', user_profile_views.render_sign_up, name="login"),
    url(r'^api/user/set_signup', user_profile_views.do_sign_up),
]
