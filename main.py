import json
import os
from flask import Flask,json, redirect, render_template, request, flash
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, login_user,login_manager, LoginManager, current_user




# my database connections
local_server = True
app = Flask(__name__)
app.secret_key = "vinuthna"



# this is for getting unique user access
login_manager = LoginManager(app)
login_manager.login_view = "login"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/covid'
db = SQLAlchemy(app)

# Config parameters (for example)
params = {
    "username": "vinu",
    "password": "vinu123"
}

@app.context_processor
def inject_params():
    return dict(params=params)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or HospitalUser.query.get(int(user_id))

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Ensure the table name matches your database
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100))
    dob = db.Column(db.String(1000))



class HospitalUser(db.Model, UserMixin):
    __tablename__ = 'hospitaluser'  # Ensure the table name matches your database
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20))
    email = db.Column(db.String(100))
    password = db.Column(db.String(1000))


class Hospitaldata(db.Model, UserMixin):
    __tablename__ = 'hospitaldata'  # Ensure the table name matches your database
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(200), unique=True)
    hname = db.Column(db.String(200))
    normalbeds = db.Column(db.Integer)
    hicubeds = db.Column(db.Integer)
    icubeds = db.Column(db.Integer)
    vbeds = db.Column(db.Integer)

class Trig(db.Model):
    __tablename__ = 'trig'
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    normalbeds=db.Column(db.Integer)
    hicubeds=db.Column(db.Integer)
    icubeds=db.Column(db.Integer)
    vbeds=db.Column(db.Integer)
    querys=db.Column(db.String(50))
    date=db.Column(db.String(50))

class BookingPatient(db.Model, UserMixin):
    __tablename__ = 'bookingpatient'  # Ensure the table name matches your database
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(20), unique=True)
    bedtype = db.Column(db.String(50))
    hcode = db.Column(db.String(50))
    spo2 = db.Column(db.Integer)
    pname = db.Column(db.String(50)) 
    pphone = db.Column(db.Integer)
    paddress = db.Column(db.String(50))



@app.route("/")
def home():

    return render_template("index.html")


@app.route("/trigers")
def trigers():
    query=Trig.query.all() 
    return render_template("trigers.html",query=query)



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        srfid = request.form.get('srf')
        email = request.form.get('email')
        dob = request.form.get('dob')
        # Encrypt the password (dob)
        encpassword = generate_password_hash(dob)
        user=User.query.filter_by(srfid=srfid).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or srfid is already exist", "warning")
            return render_template("user_signup.html")
        new_user = User(srfid=srfid, email=email, dob=encpassword)
        db.session.add(new_user)
        db.session.commit()
       
        flash("Registered Successfully! Please login...", "success")
        return render_template("userlogin.html")
        
    return render_template("user_signup.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        srfid = request.form.get('srf')
        dob = request.form.get('dob')

        user=User.query.filter_by(srfid=srfid).first()
       

        if user and check_password_hash(user.dob,dob):
            login_user(user)
            flash("Login Success", "success")
            return render_template("index.html", current_user=current_user)

            
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html")
        
    return render_template("userlogin.html")

@app.route('/hospitallogin', methods=['POST', 'GET'])
def hospitallogin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user=HospitalUser.query.filter_by(email=email).first()
       

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success", "success")
            return render_template("index.html", current_user=current_user)
            
        else:
            flash("Invalid Credentials", "danger")
            return render_template("hospitallogin.html")
        
    return render_template("hospitallogin.html")


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if 'username' in params and 'password' in params:
            if username == params['username'] and password == params['password']:
                session['user'] = username
                flash("Login success", "info")
                return render_template("addHosUser.html")
            else:
                flash("Invalid credentials", "danger")
        else:
            flash("Configuration error: Missing username or password", "danger")

    return render_template("admin.html")



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successfull", "warning")
    return redirect(url_for('login'))


@app.route('/HospitalUser', methods=['POST', 'GET'])
def hospitalUser():

    if('user' in session and session['user']==params['username']):
        
        if request.method=="POST":
            hcode = request.form.get('hcode')
            email = request.form.get('email')
            password = request.form.get('password')
            # Encrypt the password (dob)
            encpassword = generate_password_hash(password)
            hcode=hcode.upper()
            emailUser=HospitalUser.query.filter_by(email=email).first()
            if emailUser:
                flash("Email or srfid is already exist", "warning")
                
            new_user = HospitalUser(hcode=hcode, email=email, password=encpassword)
            db.session.add(new_user)
            db.session.commit()


            flash("Data Inserted Successfully","warning")
            return render_template("addHosUser.html")

        
    else:
        flash("Login and try again", "warning")
        return render_template('admin.html')
    
    
# testing whether database is connected or not
@app.route("/test")
def test():
    try:
        a = Test.query.all()
        print(a)
        return 'My database is connected'
    except Exception as e:
        print(e)
        return f'My Database is not connected {e}'

@app.route('/logoutadmin')
def logoutadmin():
    session.pop('user')
    flash("Logout Successfull", "warning")
    return render_template('admin.html')


@app.route('/addhospitalinfo', methods=['GET', 'POST'])
def addhospitalinfo():
    email=current_user.email
    posts=HospitalUser.query.filter_by(email=email).first()
    code=posts.hcode
    postdata=Hospitaldata.query.filter_by(hcode=code).first()

    if request.method == "POST":
        hcode = request.form.get('hcode')
        hname = request.form.get('hname')
        normalbeds = request.form.get('normalbeds')
        hicubeds = request.form.get('hicubeds')
        icubeds = request.form.get('icubeds')
        vbeds = request.form.get('vbeds')
        hcode = hcode.upper()
        huser = HospitalUser.query.filter_by(hcode=hcode).first()
        hduser = Hospitaldata.query.filter_by(hcode=hcode).first()

        if hduser:
            flash("Data is Already Present you can update it...","primary")
            return render_template("hospitaldata.html")
        if huser:
            new_hospital = Hospitaldata(
                hcode=hcode,
                hname=hname,
                normalbeds=int(normalbeds),
                hicubeds=int(hicubeds),
                icubeds=int(icubeds),
                vbeds=int(vbeds)
            )
            db.session.add(new_hospital)
            db.session.commit()
            flash("Data is Added", "primary")
            return redirect('/addhospitalinfo')
        else:
            flash("Hospital Code does not exist", "warning")
            return redirect('/addhospitalinfo')

    return render_template("hospitaldata.html", postdata=postdata)

@app.route("/hedit/<string:id>", methods=['POST', 'GET'])
@login_required
def hedit(id):

    if request.method == "POST":
        hcode = request.form.get('hcode')
        hname = request.form.get('hname')
        normalbeds = request.form.get('normalbeds')
        hicubeds = request.form.get('hicubeds')
        icubeds = request.form.get('icubeds')
        vbeds = request.form.get('vbeds')
        hcode = hcode.upper()
        huser = HospitalUser.query.filter_by(hcode=hcode).first()
        hduser = Hospitaldata.query.filter_by(hcode=hcode).first()
        hcode=hcode.upper()

        post=Hospitaldata.query.filter_by(id=id).first()
        post.hcode=hcode
        post.hname=hname
        post.normalbeds=normalbeds
        post.hicubeds=hicubeds
        post.icubeds=icubeds
        post.vbeds=vbeds
        db.session.commit()
        flash("Slot Updated","info")
        return redirect("/addhospitalinfo")

    posts=Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html",posts=posts)




@app.route("/hdelete/<string:id>", methods=['POST', 'GET'])
@login_required
def hdelete(id):
    post=Hospitaldata.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    flash("Date Deleted","danger")
    return redirect("/addhospitalinfo")





@app.route("/slotbooking", methods=['GET', 'POST'])
@login_required
def slotbooking():
    query = Hospitaldata.query.all()
    
    if request.method == "POST":
        srfid = request.form.get('srfid')
        bedtype = request.form.get('bedtype')
        hcode = request.form.get('hcode')
        spo2 = request.form.get('spo2')
        pname = request.form.get('pname')
        pphone = request.form.get('pphone')
        paddress = request.form.get('paddress')

        check2 = Hospitaldata.query.filter_by(hcode=hcode).first()
        checkpatient = BookingPatient.query.filter_by(srfid=srfid).first()
        
        if checkpatient:
            flash("Already SRF ID is registered", "warning")
            return render_template("booking.html", query=query)
        
        if not check2:
            flash("Hospital Code does not exist", "warning")
            return render_template("booking.html", query=query)

        code = hcode
        bedtype = bedtype
        seat = 0
        if bedtype == "NormalBed":
            seat = check2.normalbeds
            if seat > 0:
                check2.normalbeds -= 1
        elif bedtype == "HICUBed":
            seat = check2.hicubeds
            if seat > 0:
                check2.hicubeds -= 1
        elif bedtype == "ICUBed":
            seat = check2.icubeds
            if seat > 0:
                check2.icubeds -= 1
        elif bedtype == "VENTILATORBed":
            seat = check2.vbeds
            if seat > 0:
                check2.vbeds -= 1
        else:
            flash("Invalid bed type", "danger")
            return render_template("booking.html", query=query)
        
        if seat > 0:
            res = BookingPatient(srfid=srfid, bedtype=bedtype, hcode=hcode, spo2=spo2, pname=pname, pphone=pphone, paddress=paddress)
            db.session.add(res)
            db.session.commit()
            db.session.commit()
            flash("Slot is Booked kindly Visit Hospital for Further Procedure", "success")
        else:
            flash("No available beds of the selected type", "danger")

    return render_template("booking.html", query=query)

@app.route("/availablebeds", methods=['GET'])
def availablebeds():
    available_beds = Hospitaldata.query.filter(
        or_(
            Hospitaldata.normalbeds > 0,
            Hospitaldata.hicubeds > 0,
            Hospitaldata.icubeds > 0,
            Hospitaldata.vbeds > 0
        )
    ).all()  # Query to get hospital data with available beds
    return render_template("availablebeds.html", available_beds=available_beds)



@app.route("/pdetails",methods=['GET'])
@login_required
def pdetails():
    code=current_user.srfid
    data=BookingPatient.query.filter_by(srfid=code).first()
    return render_template("details.html",data=data)

  
if __name__ == '__main__':
    app.run(debug=True)
