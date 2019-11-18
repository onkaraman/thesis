import json
import final_fusion.views as ff_v
from final_fusion.models import FinalFusion
from final_fusion_column.models import FinalFusionColumn
from project.models import Project
from tq_file.models import TQFile
import tq_file.views as tq_v
from django.test import TestCase


class TestsFFModel(TestCase):
    fixtures = (
        "group.json",
        "user.json",
        "project.json"
    )

    def setUp(self):
        self.create_ff_from_scratch()

    @staticmethod
    def create_ff_from_scratch():
        project = Project.objects.first()
        project.user_profile.last_opened_project_id = project.pk
        project.user_profile.save()

        FinalFusion.objects.create(project=project)
        ff = FinalFusion.objects.first()

        # Import sample json
        json_parsed = tq_v.delegate_to_parser("sample_import_files/unsorted/items_with_duplicates.json",
                                              "json", None)
        TQFile.objects.create(
            project=project,
            source_file_name="test_1",
            display_file_name="test",
            content_json=json_parsed,
            has_been_flattened=False
        )

        tq = TQFile.objects.get(source_file_name="test_1")

        # Create FFCs
        FinalFusionColumn.objects.create(
            final_fusion=ff,
            source_tq=tq,
            source_column_name="first_name",
            display_column_name="first_name",
            rows_json=json.dumps(tq.get_column("first_name"))
        )

        FinalFusionColumn.objects.create(
            final_fusion=ff,
            source_tq=tq,
            source_column_name="last_name",
            display_column_name="last_name",
            rows_json=json.dumps(tq.get_column("last_name"))
        )

    def test_tq_column_added(self):
        """
        Check if selected TQs show as marked.
        :return:
        """
        project = Project.objects.first()
        ff = FinalFusion.objects.get(project=project)
        tq = TQFile.objects.first()

        # Check 'first_name'
        self.assertTrue(ff.tq_column_is_added("first_name", tq))
        # Check 'last_name'
        self.assertTrue(ff.tq_column_is_added("last_name", tq))

    def test_tq_column_not_added(self):
        """
        Check if unselected TQs show not as marked.
        :return:
        """
        project = Project.objects.first()
        ff = FinalFusion.objects.get(project=project)
        tq = TQFile.objects.first()

        # Check 'first_name'
        self.assertFalse(ff.tq_column_is_added("car", tq))
        # Check 'last_name'
        self.assertFalse(ff.tq_column_is_added("no_column_name", tq))

    def test_col_vars(self):
        project = Project.objects.first()
        ff = FinalFusion.objects.get(project=project)

        col_vars = ff.get_col_vars()

        # Only two vars should be present (only two cols selected in setup)
        self.assertTrue(len(col_vars))
        # Each col_var should have no more than 4 characters
        for cv in col_vars:
            self.assertTrue(len(cv) <= 4)

    def test_count_duplicates(self):
        project = Project.objects.first()
        ff = FinalFusion.objects.get(project=project)

        self.assertTrue(ff.count_duplicates(project.user_profile) > 0)

    def test_remove_duplicates(self):
        project = Project.objects.first()
        ff = FinalFusion.objects.get(project=project)

        table_w_dupes = ff_v.get_preview_table(project.user_profile)

        dupe_count = len(table_w_dupes["out_rows"])
        non_dupe_count = len(ff.remove_duplicates(table_w_dupes["out_rows"]))
        self.assertTrue(dupe_count > non_dupe_count)

