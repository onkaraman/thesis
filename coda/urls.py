from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from dashboard import views as dashboard_v
from user_profile import views as user_profile_v
from project import views as project_v
from tq_file import views as tq_v
from final_fusion import views as ff_v
from final_fusion_column import views as ffc_v
from rule_module import views as rm_v
from script_module import views as sm_v
from project_note import views as pn_v

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', dashboard_v.render_dashboard),
    url(r'^login/$', user_profile_v.render_login, name="login"),
    url(r'^signup/$', user_profile_v.render_signup),

    # Includes
    url(r'^include/user/settings/$', user_profile_v.i_render_settings),
    url(r'^include/project/new/$', project_v.i_render_new_project),
    url(r'^include/project/user_projects/$', project_v.i_render_user_projects),
    url(r'^include/tq/import/$', tq_v.i_render_import),
    url(r'^include/tq/view/$', tq_v.i_render_single_tq),
    url(r'^include/tf/preview/$', ff_v.i_render_preview_tf),
    url(r'^include/ff/export/$', ff_v.i_render_ff),

    # User API
    url(r'^api/user/signup/$', user_profile_v.do_sign_up),
    url(r'^api/user/login/$', user_profile_v.do_login),
    url(r'^api/user/logout/$', user_profile_v.do_logout),

    # Project API
    url(r'^api/project/details/$', project_v.render_project_details),
    url(r'^api/project/autoload/$', project_v.do_autoload),
    url(r'^api/project/new/$', project_v.do_create_new),
    url(r'^api/project/load/$', project_v.do_load),
    url(r'^api/project/rename/$', project_v.do_rename),
    url(r'^api/project/delete/$', project_v.do_delete_project),

    # Project notes API,
    url(r'^api/note/create/$', pn_v.do_create),
    url(r'^api/note/delete/$', pn_v.do_delete),
    url(r'^api/note/all/$', pn_v.render_all),

    # TQ API
    url(r'^api/tq/load/$', tq_v.render_all_tqs),
    url(r'^api/tq/rename/$', tq_v.do_rename),
    url(r'^api/tq/upload/$', tq_v.do_upload_tq),
    url(r'^api/tq/select_col/$', tq_v.do_select_column),
    url(r'^api/tq/select_all_col/$', tq_v.do_select_all),
    url(r'^api/tq/delete/$', tq_v.do_delete),
    url(r'^api/tq/view/$', tq_v.render_single_tq_table),

    # FFC API
    url(r'^api/ffc/rename/$', ffc_v.do_rename),

    # TF/EF API
    url(r'^api/tf/rename/$', ff_v.do_rename),
    url(r'^api/tf/preview_table/$', ff_v.render_preview_table),
    url(r'^api/tf/rm_preview_table/$', ff_v.render_preview_table_with_rm),
    url(r'^api/tf/get_col_vars/$', ff_v.do_get_col_vars),
    url(r'^api/tf/append_tables/$', ff_v.do_append_cols),
    url(r'^api/tf/remove_appended/$', ff_v.do_remove_appended),
    url(r'^api/tf/unionize_columns/$', ff_v.do_unionize_columns),
    url(r'^api/tf/count_duplicates/$', ff_v.do_count_duplicates),
    url(r'^api/tf/apply_duplicate_setting/$', ff_v.do_apply_duplicates_settings),
    url(r'^api/ff/export_visible/$', ff_v.do_check_export_button_visibility),
    url(r'^api/ff/export_content/$', ff_v.render_final_fusion),

    # RM APId
    url(r'^api/rm/get_single/$', rm_v.render_single),
    url(r'^api/rm/get_filtered/$', rm_v.render_filtered),
    url(r'^api/rm/get_all/$', rm_v.render_all_rm),
    url(r'^api/rm/transfer/$', rm_v.do_transfer_rm),
    url(r'^api/rm/create/col/$', rm_v.do_create_col_rm),
    url(r'^api/rm/edit/col/$', rm_v.do_save_edit_col),
    url(r'^api/rm/edit/row/$', rm_v.do_save_edit_row),
    url(r'^api/rm/delete/$', rm_v.do_delete_rm),
    url(r'^api/rm/create/row/$', rm_v.do_create_row_rm),
    url(r'^api/rm/rename/$', rm_v.do_rename_rm),

    # SM API
    url(r'^api/sm/validate/$', sm_v.do_validate_code),
    url(r'^api/sm/create/$', sm_v.do_create),
    url(r'^api/sm/edit/$', sm_v.do_edit),
    url(r'^api/sm/get_single/$', sm_v.render_single),
    url(r'^api/sm/delete/$', sm_v.do_delete_sm),
]






