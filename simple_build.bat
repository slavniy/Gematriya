pyinstaller -F --add-data "db;db" --add-data "templates;templates" --onefile --noconsole main.py
deactivate