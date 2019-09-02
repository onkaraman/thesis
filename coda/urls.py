from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from dashboard import views as dashboard_v
from user_profile import views as user_profile_v
from project import views as project_v
from tq_file import views as tq_v
from final_fusion import views as ff_v


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', dashboard_v.render_dashboard),
    url(r'^login/$', user_profile_v.render_login, name="login"),
    url(r'^signup/$', user_profile_v.render_signup),

    # Includes
    url(r'^include/user/settings', user_profile_v.i_render_settings),
    url(r'^include/project/new', project_v.i_render_new_project),
    url(r'^include/project/user_projects', project_v.i_render_user_projects),
    url(r'^include/tq/import', tq_v.i_render_import),
    url(r'^include/tq/view', tq_v.i_render_single_tq),

    # User API
    url(r'^api/user/signup', user_profile_v.do_sign_up),
    url(r'^api/user/login', user_profile_v.do_login),
    url(r'^api/user/logout', user_profile_v.do_logout),

    # Project API
    url(r'^api/project/new', project_v.do_create_new),
    url(r'^api/project/load', project_v.do_load),
    url(r'^api/project/rename', project_v.do_rename),
    url(r'^api/project/delete', project_v.do_delete_project),

    # TQ API
    url(r'^api/tq/load', tq_v.render_all_tqs),
    url(r'^api/tq/rename', tq_v.do_rename),
    url(r'^api/tq/upload', tq_v.do_upload_tq),
    url(r'^api/tq/delete', tq_v.do_delete),
    url(r'^api/tq/view', tq_v.render_single_tq_table),

    # Final Fusion API
    url(r'^api/ef/add_col', ff_v.do_add_column),
]

