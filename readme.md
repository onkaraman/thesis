### Thesis application
------
<b>Title</b>: Development of a web application to connect multiple data sources via control modules<br/>
<b>Author</b>: Onur Karaman<br/>
<b>Submission date</b>: November 27th, 2019

-------
This web application was written with Python, using the Django-Stack. It is intended for demonstration only and therefore should not be used for production.
Note: This app is localized for Germany (according to thesis requirements).

#### > Setup
1. Recommended: Creation of a virtual environment.
2. Install pip packages from requirements.txt (into that environment).
3. Configure a <u>psql-database</u> on your machine and enter connection data into `coda/local_settings.py`.
4. Configure web app with `python manage.py migrate`
5. Start web app with `python manage.py runserver`

#### > Registration
The web app only accepts @daimler.com email-addresses. You don't need to have an actual @daimler.com address.
For testing purposes, you can enter <something>@daimler.com as your email address (a confirmation will not be sent).

#### > Sample files
Those are located in `sample_import_files/`. The files of the two scenarios mentioned in the thesis itself are located in `sample_import_files/szen_1` and `sample_import_files/szen_2`. Instructions on how to use the scenario files are located in those folders as well.

#### > Abbrevations used in docstrings
| Abbrevation | Origin| Meaning|
| ------------- |:-------------| :-----|
| TQ | Teilquelle | One single source (of fusion) |
| TF | Teilfusion | Fusion in-progress |
| EF | Endfusion | Finished fusion |
| RM| Regelmodul | Rule module |
| SM | Script-Modul | Script rule module |

#### > Legal info
This thesis was developed during my time in Daimler AG (thesis employment). It is <u>not</u> official in-house software in any way and does <u>not</u> contain sensitive data. Yet still, I am the author of this app, which effectively makes me the copyright holder. I thank everybody who supported me during my time in Daimler.