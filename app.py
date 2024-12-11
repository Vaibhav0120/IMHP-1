from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from googletrans import Translator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

translator = Translator()

# Model for storing translation data
class Data(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    eng = db.Column(db.String(200), nullable=False)
    hin = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.eng}"

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    hin_translation = None
    try:
        if request.method == 'POST':
            eng = request.form['eng']
            hin_translation = translate_to_hindi(eng)

            # Save translation to the database
            data_entry = Data(eng=eng, hin=hin_translation)
            db.session.add(data_entry)
            db.session.commit()
    except Exception as e:
        print(f"Error in index route: {e}")
        hin_translation = "An error occurred during translation."

    alldata = Data.query.all()
    return render_template('index.html', alldata=alldata, hin_translation=hin_translation, active_page='home')

# Route to delete a specific entry
@app.route('/delete/<int:sno>')
def delete(sno):
    try:
        data_entry = Data.query.filter_by(sno=sno).first()
        if data_entry:
            db.session.delete(data_entry)
            db.session.commit()
    except Exception as e:
        print(f"Error deleting entry: {e}")
    return redirect("/")

# Route to reset translation history
@app.route('/reset_history', methods=['POST'])
def reset_history():
    try:
        Data.query.delete()
        db.session.commit()
    except Exception as e:
        print(f"Error resetting history: {e}")
    return redirect(url_for('index'))

# Route for the About page
@app.route('/about')
def about():
    return render_template('about.html', active_page='about')

# Helper function to perform translation
def translate_to_hindi(text):
    try:
        translation = translator.translate(text, src='en', dest='hi')
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return "Translation error"

# Application entry point
if __name__ == "__main__":
    try:
        with app.app_context():
            db.create_all()  # Create the 'Data' table if it doesn't exist
    except Exception as e:
        print(f"Database initialization error: {e}")

    app.run(debug=True, port=8000)
