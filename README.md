# zd2gainsight

This project is a quick and dirty Python script intended to migrate posts from a Zendesk forum to a Gainsight category. 

To run:
1. copy config_template.py to config.py
2. configure the app in config.py to your specifications
3. create your virtual environment: `virtualenv .venv`
4. activate your virtual environment: `source .venv/bin/activate`
5. install dependencies: `pip install -r requirements.txt`
6. run the script `python main.py`