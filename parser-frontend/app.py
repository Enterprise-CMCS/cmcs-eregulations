from flask import Flask, request, render_template
from wtforms import Form, IntegerField, StringField, SubmitField, validators
app = Flask(__name__)

class ParserForm(Form):
    api_key = StringField('API KEY', [validators.Length(min=5)])
    title = IntegerField('Title', [validators.Length(min=2, max=2)])
    part = IntegerField('Part', [validators.Length(min=2, max=4)])
    output = StringField('Output', default="http://localhost:8080")
    submit = SubmitField('Parse')

@app.route('/', methods=['GET', 'POST'])
def main():
    form = ParserForm(request.form)
    if request.method == 'POST' and form.validate():
        return 'Regulation Parsed!'
    return render_template('index.html', form=form) 

if __name__ == "__main__":
    app.run(host='0.0.0.0')
