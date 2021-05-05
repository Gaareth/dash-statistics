# Dash-Statistics
 
A user statistics Dashboard made with plotly dash. `(Work in progress)`


This project is heavily inspired by [Flask-Statistics](https://github.com/HealYouDown/flask-statistics) as I wanted a dashboard which is more flexible.
Therefore the ultimate goal is a dashboard where selecting different data inputs is possible.

## Design Example
<img src="https://i.imgur.com/hIsmdE9.png" alt="Design example 1" width=960 height=auto>
<img src="https://i.imgur.com/otKYm62.png" alt="Design example 2" width=960 height=auto>


## Installing

Currently only possible by cloning
``` git clone https://github.com/Gaareth/dash-statistics.git ```

## Usage

### Flask Integration

```python 
from flask import Flask
from Dash_statistics.statistics import DashStatistics

app = Flask(__name__)

stats = DashStatistics(app, prefix="/statistics/", app_name="Test")


@app.route("/")
def index():
    return ":)"

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000)

```

## Proxy

Running flask behind some webserver like Heroku will probably not give you the actual IP Address of the user. <br>
This maybe fixes this

```python
from Dash_statistics.statistics import DashStatistics
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
```

## TODO
- more flexible, either config file or store the users preferences in session variables
- pip

## Credit
Parts from the code are copied (and altered) from [Flask-Statistics](https://github.com/HealYouDown/flask-statistics). <br>
Also the design is blatantly copied.
