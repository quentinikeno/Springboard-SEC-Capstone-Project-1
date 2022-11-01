# Math Worksheet Generator

## What is this?

This app allows users to create their very own, randomly generated math worksheets.

## How does it work?

On the home page, users will be shown a form where they can specify parameters for their worksheet to be generated. Then the generated worksheet and answer key will be shown to them with options to save and download them. The user with an account will have a profile page to see all of their saved sheets, as well as options to edit or delete their account.

Any user will be able to generate a worksheet and answer key without signing up. To save and access their worksheets for later, the user will have to create an account.

## Video Demo of the App
[Demo on YouTube](https://www.youtube.com/embed/9ydG9SeEz8s)

## Deployment

Link to deployed app: https://math-worksheet-generator.herokuapp.com/

## API's Used:

[xMath API](https://x-math.herokuapp.com/)

### Technologies

-   Python 3.8.10
-   Amazon S3 Cloud Storage
-   aiohttp 3.8.1
-   arrow 1.2.2
-   boto3 1.21.43
-   Flask 2.1.1
-   Flask-Bcrypt 1.0.1
-   Flask-DebugToolbar 0.13.1
-   Flask-SQLAlchemy 2.5.1
-   Flask-WeasyPrint 0.6
-   Flask-WTF 1.0.1
-   JQuery 3.6

## Installing on your Machine

First clone or download this repository.

Next in the directory where the project is located, create a virtual environment and install the requirements using PIP.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If PostgreSQL is not on your machine, go ahead and install it now.  Make sure the PostgreSQL server is running and create two databases one for the main app and one for running tests.  On Ubuntu for the commands for this would be:

```
sudo service postgresql start
createdb worksheet_generator # DB for main app.
createdb worksheet_generator_test # DB for running tests.
```

On Ubuntu install PangoCairo.
```
sudo apt-get install libpangocairo-1.0-0
```

Finally, start the Flask App and open it in your favorite browser.
```
flask run
```

## Tests

You can run all tests using unittest.

```
python3 -m unittest
```

## Author

Quentin Ikeno
