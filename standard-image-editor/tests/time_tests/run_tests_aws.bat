cd ../../
python script_set_configuration.py AWS
start script_start_local_apps.bat
cd tests/time_tests
timeout /t 12
pytest . -v --count=49
