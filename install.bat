@ECHO OFF
TITLE Batt_Base alpha version installer

pip install virtualenv
virtualenv batt_base_env
.\venv\Scripts\activate
pip install -r requirements.txt
flask db init
flask db migrate
flask db upgrade
python -m db_init
        
@pause