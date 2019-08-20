from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from dashboard import views as dashboard_v
from user_profile import views as user_profile_v
from project import views as project_v

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', dashboard_v.render_dashboard),
    url(r'^login/$', user_profile_v.render_login, name="login"),
    url(r'^signup/$', user_profile_v.render_signup),

    url(r'^include/user/settings', user_profile_v.render_settings),

    url(r'^api/user/signup', user_profile_v.do_sign_up),
    url(r'^api/user/login', user_profile_v.do_login),
    url(r'^api/user/logout', user_profile_v.do_logout),

    url(r'^api/project/new', project_v.do_create_new),
]
