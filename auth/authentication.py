from flask import Flask, Blueprint, render_template, url_for, request, redirect, session, current_app
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
import re
import os
import random
import string
from datetime import timedelta
from auth.dbcon import connect

authentication = Blueprint("authentication", __name__, static_folder="../static", template_folder="templates")

# session.permanent_session_lifetime = timedelta(days = 5)

def change_session(username, email):
    session['username'] = username
    session['email'] = email


def authenticated():
    if 'email' in session:
        return True, session['user']
    else:
        return False, -1

def logoutUser():
    session['loggedin'] = False
    session.pop('user', None)
    session.pop('username', None)
    session.pop('email', None)


def calculateVerficationID(cursor):
    

    verificationidAlreadyUsed = False
    while not verificationidAlreadyUsed:
            try:
                verificationid = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
                
                cursor.execute("SELECT count(*) FROM REGISTEREDUSERS WHERE VERIFYLINKID = ?", verificationid)

                if cursor.fetchone()[0] > 0:
                    continue
            
                verificationidAlreadyUsed = True
            except:
                print("ERROR!! EMAIL VERIFICATION ID")
    
    return verificationid

def sendMail(verificationid,firstName,email):
    current_app.config['MAIL_SERVER']='smtp.gmail.com'
    current_app.config['MAIL_PORT'] = 465
    current_app.config['MAIL_USERNAME'] = os.environ['EMAIL_ADDRESS']
    current_app.config['MAIL_PASSWORD'] = os.environ['EMAIL_PASSWORD']
    current_app.config['MAIL_USE_TLS'] = False
    current_app.config['MAIL_USE_SSL'] = True
    mail = Mail(current_app)

    msg = Message("Confirm your 'Restaurant Recommendation' account", sender='noreply@planvisit.com', recipients = ["arnold.raphael@web.de"])
    url = request.url_root + '/authentication/' + verificationid
    msg.html = render_template('mail.html', firstName = firstName, link = url)
    mail.send(msg)

def emailFormatErr(email):
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    return not re.fullmatch(regex, email)

@authentication.route('/login')
def login():
    return render_template('login.html')

@authentication.route('/login', methods = ['POST'])
def login_post():
    req = request.form

    email = req["emailaddress"]
    password = req["passwordlogin"]

    if emailFormatErr(email):
        return render_template('login.html', passwordError = 'Not an email!!')
    else:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute("SELECT R.IDUSER,FIRSTNAME,LASTNAME,USERNAME,PASSWORD,VERIFIED FROM REGISTEREDUSERS R join Users U on R.IDUSER = U.IDUSER WHERE EMAIL=?",email)
        
        i = 0
        iduser = 0
        authfirstName = ''
        authlastName = ''
        username = ''
        pwhash = ''
        verified = -1

        for row in cursor.fetchall():
            if i > 0:
                return render_template('login.html', passwordError = 'Error, pls contact us!')
            iduser = row[0]
            authfirstName = row[1]
            authlastName = row[2]
            username = row[3]
            pwhash = row[4]
            verified = int(row[5])
            i = i + 1

        if verified == 0:
            return render_template('login.html', passwordError = 'Please verify your account Have a look in your email account!')

        if authfirstName == '':
            return render_template('login.html', passwordError = 'No such email!')
        
        if not check_password_hash(pwhash, password):
            return render_template('login.html', passwordError = 'Wrong password!')


        session_permanent = True
        session['loggedin'] = True
        session['user'] = iduser
        
        session['username'] = username
        session['email'] = email

        connection.commit()
        connection.close()
        return redirect('/home')

@authentication.route('/register')
def register():
    return render_template('register.html')

@authentication.route('/register', methods=['POST'])
def register_post():
    req = request.form

    firstName = req["firstName"]
    lastName = req["lastName"]
    email = req["email"]
    username = req["username"]
    password = req["password"]
    passwordVerification = req["passwordVerification"]

    if firstName=='':
        #inform user
        firstNameForgot = 'Forgot to insert First Name!'
        return render_template('register.html', firstNameForgot = firstNameForgot)
        
    elif lastName=='':
        #inform user
        lastNameForgot = 'Forgot to insert Last Name!'
        return render_template('register.html', lastNameForgot = lastNameForgot)
    elif emailFormatErr(email):
        #inform user
        emailFormatError = 'Is not an email!'
        return render_template('register.html', emailFormatError = emailFormatError)
    elif username=='':
        #inform user
        usernameError = 'Username is already used!'
        return render_template('register.html', usernameError = usernameError)
    elif password != passwordVerification:
        # inform user
        passwordError = 'Passwords are not the same!'
        return render_template('register.html', passwordError = passwordError)
    elif len(password) < 8:
        return render_template('register.html', passwordError = 'Password must have at least 8 signs')
    else:
        # database entry
        verificationid = ''
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute("SELECT count(*) FROM REGISTEREDUSERS WHERE EMAIL=?",email)
        if cursor.fetchone()[0] > 0:
            connection.commit()
            connection.close()
            return render_template('register.html', emailFormatError = 'Account with the email '+ email + ' already exists!')
    	
        verificationid = calculateVerficationID(cursor)


        password = generate_password_hash(password, method="sha256")

        #what if there is someone in between!
        cursor.execute("INSERT INTO USERS(USERNAME) values(?)",username)
        cursor.execute("INSERT INTO REGISTEREDUSERS(IDUSER,FIRSTNAME,LASTNAME,EMAIL,PASSWORD,VERIFYLINKID) VALUES(IDENT_CURRENT('USERS'),?,?,?,?,?)",firstName,lastName,email,password,verificationid)
        

        connection.commit()
        connection.close()

        # send verification mail to applicant
        sendMail(verificationid,firstName,email)
        return render_template('registersuccess.html')

@authentication.route('/<verificationid>')
def verficationID(verificationid):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("SELECT IDUSER,VERIFIED FROM REGISTEREDUSERS WHERE VERIFYLINKID = ?",verificationid)
    row = cursor.fetchone()
    iduser = row[0]
    verified = row[1]
    

    if verified == 0:
        cursor.execute("UPDATE REGISTEREDUSERS SET VERIFIED = ? WHERE IDUSER = ?",1,iduser)

    connection.commit()
    connection.close()
    return render_template('accountconfirmation.html', verified = verified)

        

@authentication.route('/logout')
def logout():
    logoutUser()
    return redirect('/home')