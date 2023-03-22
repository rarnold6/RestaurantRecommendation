from flask import Flask, render_template, url_for, request, redirect, session

from auth.authentication import authentication
from flask_mail import Mail, Message
from main.public import public


app = Flask(__name__)
    

#make it a better key!
app.secret_key = "itsacomplexkey"



app.register_blueprint(authentication, url_prefix="/authentication")
app.register_blueprint(public)




"""@app.route('/registersuccess')
def registrationsuccess():
    return render_template('registersuccess.html')"""


if __name__ == "__main__":
   app.run(debug=True)