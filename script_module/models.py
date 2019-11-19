import re
from django.db import models
from django.utils import timezone
from final_fusion.models import FinalFusion


class ScriptModule(models.Model):
    """
    Script-rule modules have their own class since they work in a different way.
    Instead of saving when- and then-data, objects of this class only need scripts to execute.
    """
    creation_date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=40, default="Script Module")
    final_fusion = models.ForeignKey(FinalFusion, on_delete=models.CASCADE)
    code_content = models.CharField(max_length=900)

    def check_validity(self):
        """
        Will check whether this object's code content is valid. Validity rules are
        1: No import statements, 2: No eval(), exec() or print() calls,
        3: No _row structure changes (i. e. you can't edit the dictionary which represents the row itself).
        Otherwise, it will check if the passed code will work as Python code.
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
            if "float(" not in self.code_content:
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
        Will check whether the the _row-dictionary itself has been modified.
        """
        exec_vars = {"_row": self.final_fusion.get_col_vars()}
        pre_imports = "import math, re, random\n"
        code_content = "%s%s" % (pre_imports, self.code_content)

        exec(code_content, globals(), exec_vars)

        if "_row" not in exec_vars:
            return False

        for k in self.final_fusion.get_col_vars().keys():
            if k not in exec_vars["_row"]:
                return False
        return True

    def apply_to_row(self, row, edit_style, changes_visible):
        """
        Will apply the code of this rm to the passed row parameter. Will prepare the code (by adding imports),
        and then execute it on the row, which itself will be passed via 'exec_vars'. After completion, the modified
        row values will be re-applied to the row itself (the code uses only short-hands for row names).
        """
        orig = row.copy()
        exec_vars = {"_row": row, "_append": False}
        pre_imports = "import math, re, random\n"
        code_content = "%s%s" % (pre_imports, self.code_content)

        # Replace long var names with short var names so the script can interpret user input
        cv = self.final_fusion.get_col_vars()
        for k in cv.keys():
            if not (".SUM" in k or ".AVG" in k):
                row[k] = row.pop(cv[k])
            else:
                row[k] = cv[k]

        try:
            exec(code_content, globals(), exec_vars)
        except KeyError as ke:
            pass

        for k in cv.keys():
            # Reverse name linking
            if not (".SUM" in k or ".AVG" in k):
                row[cv[k]] = row.pop(k)

                if row[cv[k]] != orig[cv[k]]:
                    if changes_visible:
                        if exec_vars["_append"] and orig[cv[k]] is not "-":
                            row[cv[k]] = "%s, %s" % (orig[cv[k]], (edit_style % row[cv[k]]))
                        else:
                            row[cv[k]] = edit_style % row[cv[k]]
                    else:
                        if exec_vars["_append"] and orig[cv[k]] is not "-":
                            row[cv[k]] = "%s, %s" % (orig[cv[k]], row[cv[k]])
                        else:
                            row[cv[k]] = row[cv[k]]

    def __str__(self):
        return "#%d: %s" % (self.pk, self.name)