import os

from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from forms import CreateWorksheetForm

import asyncio
import aiohttp

app = Flask(__name__)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "very secret key")
toolbar = DebugToolbarExtension(app)

X_MATH_API_BASE_URL = "https://x-math.herokuapp.com/api"

def get_tasks(session, operations, number_questions):
    """Create a list of tasks for asyncio to perform asynchronously."""
    tasks = []
    for i in range(number_questions):
        tasks.append(session.get(f"{X_MATH_API_BASE_URL}/{operations}", ssl=False))
    return tasks

async def get_math_data(operations, number_questions):
    """Asynchronously call math api to return a list of math expressions."""
    results = []
    async with aiohttp.ClientSession() as session:
            tasks = get_tasks(session, operations, number_questions)
            responses = await asyncio.gather(*tasks)
            for response in responses:
                results.append(await response.json())
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CreateWorksheetForm()
    
    if form.validate_on_submit():
        name = form.name.data
        operations = form.operations.data
        number_questions = int(form.number_questions.data)
        
        asyncio.run(get_math_data(operations, number_questions))
        
        print(name, operations, number_questions)
    
    return render_template('index.html', form=form)
 