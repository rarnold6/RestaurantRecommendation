from flask import Blueprint, render_template, url_for, session, redirect, request
from auth.authentication import authenticated,calculateVerficationID,sendMail,logoutUser,change_session
from auth.dbcon import connect
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from datetime import datetime,timedelta


public = Blueprint("public", __name__, static_folder="../static", template_folder="templates")

@public.route('/')
@public.route('/home')
def homepage():
    user = authenticated()
    if user[0]:
        print(user[1])
        
    return render_template('homepage.html')

@public.route('/plan_new_visit')
def plan_new_visit():
    user = authenticated()
    if user[0]:
        now = datetime.now()
        max = now + timedelta(days = 30)
        nowString = now.strftime("%Y-%m-%dT%H:%M")
        maxString = max.strftime("%Y-%m-%dT%H:%M")
        return render_template('plan_new_visit.html', now = nowString, min = nowString, max = maxString)
    else: 
        return redirect('/authentication/login')

@public.route('/plan_new_visit', methods = ['POST'])
def plan_new_visit_post():
    user = authenticated()
    if user[0]:
        linkidAlreadyUsed = False
        linkid = ''

        now = datetime.now()
        nowString = now.strftime("%Y-%m-%dT%H:%M:%S")

        req = request.form

        label = req["labelVisit"]
        if label == '':
            return render_template('plan_new_visit.html', labelVisit = 'Please label your visit!')

        checkbox = req.get("dateDefined")
        if checkbox == "on":
            dateBegin = req["meeting-time"]
            dateBegin = dateBegin + ":00"
            print(dateBegin)
            connection = connect()
            cursor = connection.cursor()

            while not linkidAlreadyUsed:
                try:
                    linkid = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
                    cursor.execute(" INSERT INTO RESTAURANTVISIT(IDUSER,LINKID,DATECREATED,LABEL,FINALDATE) values (?,?,?,?,?)",user[1],linkid,nowString,label,dateBegin)
                    linkidAlreadyUsed = True
                    print(linkid)
                except:
                    continue

            connection.commit()
            connection.close()

            link = request.url_root + '/plannedvisit/' + linkid
            return render_template('plan_new_visit.html', linkgenerated = True, linkid = linkid, link = link)

        else:
            dateListFrom = req.getlist("meeting-time-from[]")
            dateListUntil = req.getlist("meeting-time-until[]")
            
            length = len(dateListFrom)
            while length > 0:
                dateListFrom[length-1] = dateListFrom[length-1] + ":00"
                dateListUntil[length-1] = dateListUntil[length-1] + ":00"
                length = length-1

            connection = connect()
            cursor = connection.cursor()

            while not linkidAlreadyUsed:
                try:
                    linkid = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
                    cursor.execute("INSERT INTO RESTAURANTVISIT(IDUSER,LINKID,DATECREATED,LABEL) values (?,?,?,?)",user[1],linkid,nowString,label)
                    linkidAlreadyUsed = True
                except:
                    continue

            length = len(dateListFrom)
            while length > 0:
                print(dateListFrom[length-1])
                idtimeslot = -1
                try:
                    cursor.execute("INSERT INTO TIMESLOTS(STARTTIME,ENDTIME) VALUES(?,?)",dateListFrom[length-1],dateListUntil[length-1])
                except: 
                    cursor.execute("SELECT IDTIMESLOT FROM TIMESLOTS WHERE STARTTIME = ? and ENDTIME = ?",dateListFrom[length-1],dateListUntil[length-1])
                    idtimeslot = cursor.fetchone()[0]


                if length == len(dateListFrom):
                    cursor.execute("INSERT INTO VISITPLANNING(IDRESTAURANTVISIT,IDUSER) VALUES (IDENT_CURRENT('RESTAURANTVISIT'),?)",int(user[1]))
                if idtimeslot == -1:
                    cursor.execute("INSERT INTO POSSIBLETIMESLOTS(IDRESTAURANTVISIT,IDUSER,IDTIMESLOT) VALUES(IDENT_CURRENT('RESTAURANTVISIT'),?,IDENT_CURRENT('TIMESLOTS'))",int(user[1]))
                else: 
                    cursor.execute("INSERT INTO POSSIBLETIMESLOTS(IDRESTAURANTVISIT,IDUSER,IDTIMESLOT) VALUES(IDENT_CURRENT('RESTAURANTVISIT'),?,?)",int(user[1]),idtimeslot)
                length = length-1

            connection.commit()
            connection.close()

            link = request.url_root + 'plannedvisit/' + linkid
            return render_template('plan_new_visit.html', linkgenerated = True, linkid = linkid, link = link)

    else:
        return redirect('/authentication/login')

@public.route('/plannedvisits')
def plannedvisits():
    user = authenticated()
    if user[0]:
        connection = connect()
        cursor = connection.cursor()

        cursor.execute("SELECT LABEL,LINKID,DATECREATED FROM RESTAURANTVISIT WHERE IDUSER=?",user[1])

        data = cursor.fetchall()

        return render_template('plannedvisits.html', data = data)
    else:
        return redirect('/home')

@public.route('/plannedvisit/<visitid>', methods = ["GET","POST"])
def plannedvisitID(visitid):
    

    if len(visitid) != 20:
        return redirect('/home')

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("SELECT IDRESTAURANTVISIT,IDUSER,FINALDATE FROM RESTAURANTVISIT WHERE LINKID = ?",visitid)
    idrestaurantvisit = -1
    iduser = -1
    finaldate = ''
    
    row = cursor.fetchone()
    
    try:
        idrestaurantvisit = int(row[0])
        iduser = int(row[1])
        finaldate = row[2]
    except:
        connection.commit()
        connection.close()
        return redirect('/home')

    if request.method == "GET":
        user = authenticated()
        loggedinuserid = -1
        if user[0]:
            loggedinuserid = int(user[1])

        if finaldate == None and iduser != loggedinuserid:
            
            cursor.execute("SELECT t.STARTTIME, t.ENDTIME FROM POSSIBLETIMESLOTS p join TIMESLOTS t on p.IDTIMESLOT = t.IDTIMESLOT WHERE p.IDUSER = ? AND p.IDRESTAURANTVISIT = ?",iduser,idrestaurantvisit)
            rowsTimes = cursor.fetchall()

            connection.commit()
            connection.close()
            length = len(rowsTimes)

            while length > 0:
                rowsTimes[length-1][0] = rowsTimes[length-1][0].strftime("%Y-%m-%dT%H:%M")
                rowsTimes[length-1][1] = rowsTimes[length-1][1].strftime("%Y-%m-%dT%H:%M")
                length = length - 1

            return render_template('survey.html', rows = rowsTimes, notadmin = True, dateNotDefined = True)
        elif finaldate == None:
            connection.commit()
            connection.close()
            return render_template('survey.html', notadmin = False)
        else:
            connection.commit()
            connection.close()

            finaldate = finaldate.strftime("%Y-%m-%d %H:%M")
            dateList = finaldate.split(' ')

            return render_template('survey.html', dateNotDefined = False, finalDate = dateList[0], time = dateList[1], notadmin = True)
    
    else:
        user = authenticated()
        req = request.form
        username = ''

        #if there is a not loggedin user, create new user
        if not user[0]:
            username = req["username"]
            if username == '':
                return redirect('/plannedvisit/' + visitid)
            cursor.execute("INSERT INTO USERS(USERNAME) VALUES (?);",username)
            cursor.execute("SELECT IDENT_CURRENT('USERS');")
            loggedinuserid = cursor.fetchone()[0]

        if finaldate == None and iduser != loggedinuserid:
            startingTimesList = req.getlist("startingTimes[]")
            endingTimesList = req.getlist("endingTimes[]")
            checkboxConfirmList = req.getlist("dateConfirm[]")
            checkboxDeleteList = req.getlist("dateDelete[]")

            print(username)
            print(checkboxConfirmList)
            print(checkboxDeleteList)
            
            i = 0
            j = 0
            index = 0
            lenconfirm = len(checkboxConfirmList)
            lendelete = len(checkboxDeleteList)
            cursor.execute("SELECT T.IDTIMESLOT,STARTTIME,ENDTIME  FROM POSSIBLETIMESLOTS P join TIMESLOTS T on P.IDTIMESLOT = T.IDTIMESLOT WHERE P.IDRESTAURANTVISIT = ? and P.IDUSER = ?",idrestaurantvisit, iduser)
            rows = cursor.fetchall()

            while index < len(startingTimesList):
                if lenconfirm > 0 and int(checkboxConfirmList[i]) == index:
                    i = i + 1
                elif lendelete > 0 and int(checkboxDeleteList[j]) == index:
                    j = j + 1
                else:
                    """changed = False
                    if (startingTimesList[index] + ":00") != str(rows[index][1]):
                        rows[index][1] = startingTimesList[index] + ":00"
                        changed = True
                    if (endingTimesList[index] + ":00") != str(rows[index][2]):
                        rows[index][2] = endingTimesList[index] + ":00"
                        changed = True
                    if changed:
                        """
                    index = index + 1
                    print('hello')


            """while index < len(startingTimesList):
                if lenconfirm > 0 and int(checkboxConfirmList[i]) == index:
                    print()
                    i = i + 1
                elif lendelete > 0 and int(checkboxDeleteList[j]) == index:
                    print(j)
                    j = j + 1
                else:
                    print('hello')
                index = index + 1"""
            



            



        else:
            print("hello")
        return render_template('surveyconfirmation.html')

@public.route('/profile')
def profile():
    user = authenticated()
    if user[0]:
        connection = connect()
        cursor = connection.cursor()

        cursor.execute("SELECT FIRSTNAME,LASTNAME,EMAIL,USERNAME FROM REGISTEREDUSERS R join USERS U on R.IDUSER = U.IDUSER WHERE R.IDUSER = ?",user[1])

        row = cursor.fetchone()
        
        connection.commit()
        connection.close()

        return render_template('profile.html', firstName = row[0], lastName = row[1], email = row[2], username = row[3])
    else:
        return redirect('/login')

@public.route('/profile', methods=["POST"])
def profile_post():
    req = request.form
    firstName = req["firstName"]
    lastName = req["lastName"]
    username = req["username"]
    email = req["email"]
    street = req["street"]
    housenumber = req["houseNumber"]
    zipcode = req["zipCode"]

    user = authenticated()
    if user[0]:
        connection = connect()
        cursor = connection.cursor()

        cursor.execute("SELECT EMAIL,LATITUDE,LONGITUDE FROM REGISTEREDUSERS WHERE IDUSER = ?",user[1])
        row = cursor.fetchone()

        if row[1] == None and row[2] == None:
            print("Hello")

        if row[0] != email:

            cursor.execute("UPDATE USERS SET USERNAME = ? WHERE IDUSER = ?",username,user[1])

            verificationID = calculateVerficationID(cursor)

            cursor.execute("UPDATE REGISTEREDUSERS SET FIRSTNAME = ?, LASTNAME = ?, EMAIL = ?, VERIFIED = 0, VERIFYLINKID = ? WHERE IDUSER = ?",firstName,lastName,email,verificationID,user[1])
            connection.commit()
            connection.close()

            sendMail(verificationID,firstName,email)

            logoutUser()
            return render_template('changed_success.html', type = 'Mail')


        else:

            cursor.execute("UPDATE USERS SET USERNAME = ? WHERE IDUSER = ?",username,user[1])
            cursor.execute("UPDATE REGISTEREDUSERS SET FIRSTNAME = ?, LASTNAME = ?",firstName,lastName)

            change_session(username,email)
            
            connection.commit()
            connection.close()

            return redirect('/profile')

@public.route('/changePassword')
def changePassword():
    user = authenticated()
    if user[0]:
        return render_template('change_password.html')
    else:
        return redirect('/home')

@public.route('/changePassword', methods=["POST"])
def changePassword_post():
    user = authenticated()
    if user[0]:
        req = request.form
        oldPassword = req["oldPassword"]
        newPassword = req["newPassword"]
        confirmNewPassword = req["confirmNewPassword"]

        if newPassword != confirmNewPassword:
            return render_template('change_password.html',passwordError = 'New password and confirmed new password are not the same!')

        connection = connect()
        cursor = connection.cursor()

        cursor.execute("SELECT PASSWORD FROM REGISTEREDUSERS WHERE IDUSER = ?",user[1])
        
        oldPasswordStored = cursor.fetchone()[0]

        if not check_password_hash(oldPasswordStored, oldPassword):
            connection.commit()
            connection.close()
            return render_template('change_password.html', passwordError = 'Wrong old password!')

        hashedPassword = generate_password_hash(newPassword, method="sha256")

        cursor.execute("UPDATE REGISTEREDUSERS SET PASSWORD = ? WHERE IDUSER = ?",hashedPassword,user[1])

        connection.commit()
        connection.close()



        return render_template('changed_success.html',type = 'Password')
    else:
        return redirect('/home')

            
        

