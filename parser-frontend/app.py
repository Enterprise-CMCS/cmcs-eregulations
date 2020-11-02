from flask import Flask, request, render_template
from wtforms import Form, IntegerField, StringField, SubmitField, validators
import os
from subprocess import Popen, PIPE
app = Flask(__name__)

def reg_parser(api_key, title, part, output):
    # change directory
    source = os.path.dirname(__file__)
    parent = os.path.join(source, '../')
    script_path = os.path.join(parent, 'load_data.sh')
    # run load_data.sh
    script = [script_path, api_key, 'pipeline', title, part, output]
    print(script)
    out = Popen(script, stdout=PIPE, shell=True)
    return out.stdout.read()

class ParserForm(Form):
    api_key = StringField('API KEY', [validators.Length(min=5)])
    title = StringField('Title', [validators.Length(min=2, max=2)])
    part = StringField('Part', [validators.Length(min=2, max=4)])
    output = StringField('Output', default="http://localhost:8080")
    submit = SubmitField('Parse')

@app.route('/', methods=['GET', 'POST'])
def main():
    form = ParserForm(request.form)
    if request.method == 'POST' and form.validate():
        api_key = form.api_key.data
        title = form.title.data
        part = form.part.data
        output = form.output.data
        # return ("Regulation %s %s parsed to %s." % (title, part, output))
        return reg_parser(api_key, title, part, output)
    return render_template('index.html', form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
