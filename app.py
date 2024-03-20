from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from googletrans import Translator


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

translator = Translator()

class Data(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    eng = db.Column(db.String(200), nullable=False)
    hin = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.eng}"

@app.route('/', methods=['GET', 'POST'])
def index():
    hin_translation = None
    if request.method == 'POST':
        eng = request.form['eng']
        hin_translation = translate_to_hindi(eng)

        data_entry = Data(eng=eng, hin=hin_translation)
        db.session.add(data_entry)
        db.session.commit()

    alldata = Data.query.all()
    return render_template('index.html', alldata=alldata, hin_translation=hin_translation, active_page='home')

@app.route('/delete/<int:sno>')
def delete(sno):
    data_entry = Data.query.filter_by(sno=sno).first()
    db.session.delete(data_entry)
    db.session.commit()
    return redirect("/")

@app.route('/reset_history', methods=['POST'])
def reset_history():
    Data.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html', active_page='about')

def translate_to_hindi(text):
    try:
        translation = translator.translate(text, src='en', dest='hi')
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return "Translation error"

if __name__ == "__main__":
    with app.app_context():
        # Create the 'Data' table in the database
        db.create_all()

    app.run(debug=True, port=8000)
