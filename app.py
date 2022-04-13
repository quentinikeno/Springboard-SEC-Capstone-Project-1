import os

from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from forms import CreateWorksheetForm

app = Flask(__name__)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "very secret key")
toolbar = DebugToolbarExtension(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CreateWorksheetForm()
    
    if form.validate_on_submit():
        name = form.name.data
        operations = form.operations.data
        number_questions = form.number_questions.data
        
        print(name, operations, number_questions)
    
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 