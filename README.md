## Run CLI
python .\management\inventory_tool.py

## Run the Application
python -m app.main

## Run UI JS App
python -m http.server 8080

## Run Tests
python -m pytest .\app\tests\test_inventory.py -v
python -m pytest .\app\tests -v

## Update the requirements list
pip freeze > requirement.txt

## Prevent common web vulnerabilities using security headers
pip install Secweb

## Rate limiting using SlowAPI
pip install slowapi

