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
        json_parsed = tq_v.delegate_to_parser("sample_import_files/unsorted/cars.json",
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
        tq_table = TQFile.objects.first().get_as_table(project.user_profile)

        # Check 'first_name'
        self.assertTrue(tq_table["cols"][1]["ef_added"])
        # Check 'last_name'
        self.assertTrue(tq_table["cols"][2]["ef_added"])
