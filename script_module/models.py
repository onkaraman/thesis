import re
from django.db import models
from django.utils import timezone
from final_fusion.models import FinalFusion


class ScriptModule(models.Model):
    """
    ScriptModule
    """
    creation_date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=40, default="Script Module")
    final_fusion = models.ForeignKey(FinalFusion, on_delete=models.CASCADE)
    code_content = models.CharField(max_length=900)

    def check_validity(self):
        """
        check_validity
        """
        msg = []

        for l in self.code_content.split("\n"):
            # Import statements
            if re.search(r'^import \w+$', l):
                msg.append("Import statements not allowed")
                break

            if re.search(r'^eval\(', l):
                msg.append("eval() not allowed")
                break

            if re.search(r'^exec\(', l):
                msg.append("exec() not allowed")
                break

            if re.search(r'^print\(', l):
                msg.append("print() not allowed")
                break

        try:
            # Check if all _row entries are still there
            if not self.row_structure_retained():
                msg.append("_row structure change not allowed")
        except ValueError as verr:
            # Only do exception if it's because of a float
            if "float(" not in self.code_content or "int(" not in self.code_content:
                msg.append(verr.args[0])

        except Exception as exc:
            msg.append("Python code is invalid")
            if exc.args:
                msg.append(exc.args[0])

        # Fair warnings
        valid = len(msg) == 0
        if valid:
            msg.append("Script is valid and ready to use.")
        if valid and not re.search(r'_row\[\"\w+\"\]', self.code_content):
            msg.append("Script is probably useless.")

        return {
            "valid": valid,
            "msg": msg
        }

    def row_structure_retained(self):
        """
        row_structure_retained
        """
        exec_vars = {"_row": self.final_fusion.get_col_vars()}
        exec(self.code_content, globals(), exec_vars)

        if "_row" not in exec_vars:
            return False

        for k in self.final_fusion.get_col_vars().keys():
            if k not in exec_vars["_row"]:
                return False
        return True

    def apply_to_row(self, row, edit_style, changes_visible):
        """
        apply_to_row
        """
        orig = row.copy()
        exec_vars = {"_row": row}
        pre_imports = "import math, re, random\n"
        code_content = "%s%s" % (pre_imports, self.code_content)

        cv = self.final_fusion.get_col_vars()
        for k in cv.keys():
            row[k] = row.pop(cv[k])

        try:
            exec(code_content, globals(), exec_vars)
        except KeyError as ke:
            pass

        for k in cv.keys():
            row[cv[k]] = row.pop(k)
            if row[cv[k]] != orig[cv[k]]:
                if changes_visible:
                    row[cv[k]] = edit_style % row[cv[k]]

    def __str__(self):
        return "#%d: %s" % (self.pk, self.name)