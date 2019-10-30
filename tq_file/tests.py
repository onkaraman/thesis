import json
import tq_file.views as tq_v
from django.test import TestCase
from tq_file.models import TQFile
from project.models import Project


class TestsTQImport(TestCase):
    def test_valid_json(self):
        json_parsed = tq_v.delegate_to_parser("sample_import_files/unsorted/cars.json",
                                              "json", None)

        self.assertTrue(len(json.loads(json_parsed)) > 0)

    def test_invalid_json(self):
        json_parsed = tq_v.delegate_to_parser("sample_import_files/border_cases/wrong_syntax.json",
                                              "json", None)
        self.assertFalse(json_parsed)

    def test_sheet_preparse(self):
        sheet_list = tq_v.preparse_get_sheets("sample_import_files/unsorted/user_city.xlsx", "xlsx")

        self.assertTrue(len(sheet_list) > 0)
        self.assertTrue(type(sheet_list) == list)


class TestsTQModel(TestCase):
    fixtures = (
        "group.json",
        "user.json",
        "project.json",
        "ff.json",
        "tqfile.json"
    )

    def test_get_as_table(self):
        json_parsed = tq_v.delegate_to_parser("sample_import_files/unsorted/cars.json",
                                              "json", None)

        TQFile.objects.create(
            project=Project.objects.first(),
            source_file_name="test",
            display_file_name="test",
            content_json=json_parsed,
            has_been_flattened=False
        )
        profile = Project.objects.first().user_profile
        profile.last_opened_project_id = 1
        profile.save()

        tq = TQFile.objects.last()
        table = tq.get_as_table(profile)

        # Check that essentials are in column data
        first_col = table["cols"][0]
        self.assertTrue("ef_added" in first_col)
        self.assertTrue(first_col["name"] == "#")

        # Check row data
        self.assertTrue(len(table["rows"]) > 0)
        self.assertTrue(type(table["rows"][0]) == dict)

    def test_get_column(self):
        json_parsed = tq_v.delegate_to_parser("sample_import_files/unsorted/cars.json",
                                              "json", None)

        TQFile.objects.create(
            project=Project.objects.first(),
            source_file_name="test",
            display_file_name="test",
            content_json=json_parsed,
            has_been_flattened=False
        )
        profile = Project.objects.first().user_profile
        profile.last_opened_project_id = 1
        profile.save()

        tq = TQFile.objects.last()
        col = tq.get_column("first_name")

        self.assertTrue(type(col) == list)
        self.assertTrue(len(col) > 0)
