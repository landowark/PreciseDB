from flask import Flask
import namer


app = Flask(__name__)

@app.route('/add')
def add_sample():
   return namer.parsePatient("789")

if __name__ == '__main__':
    app.run(debug=True)