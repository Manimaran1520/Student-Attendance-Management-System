from flask import Flask,flash, render_template, request,url_for,redirect,Response,redirect,session
import numpy as np
import face_recognition
from functools import wraps
import cv2
import os
from datetime import datetime
import sqlite3 as sql
import urllib
import requests

'''
pip install flask
pip install face_recognition
pip install opencv

'''
app = Flask(__name__)


#yyyy-mm-dd to dd-mm-yyyy   
def date_db_to_user(date):
    return datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')
 
#dd-mm-yyyy  to yyyy-mm-dd
def date_user_to_db(date):
    return datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
    
    
#define function for convert yyyy-mm-dd to dd-mm-yyyy
def format_datetime(value, format="%d-%m-%Y"):
    if value is None:
        return ""
    return datetime.strptime(value,"%Y-%m-%d").strftime(format)
 
#configured Jinja2 environment with user defined
app.jinja_env.filters['date_format']=format_datetime
 
#check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'isLogged' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorized, Please Login','danger')
			return redirect(url_for('index'))
	return wrap
 
@app.route('/')
@app.route('/indx')
def indx():
    return render_template("indx.html")
 
#index 

@app.route('/index',methods=['GET','POST'])
def index():
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    if request.method=='POST':  
        if request.form['admin_submit']=="Admin Login":
            uname=request.form['email']
            upass=request.form['upass']
            cur.execute("select * from admin where ANAME=? and APASS=?",(uname,upass))
            data=cur.fetchone()
            if data:
                session['isLogged']=True
                flash('Login Successfully','success')
                return redirect('department')
            else:
                flash('Invalid Login. Enter Correct Login Details','danger')
            cur.close()
        if request.form['admin_submit']=="Staff Login":
            uname=request.form['s_email']
            upass=request.form['s_upass']
            cur.execute("select * from staff where SNAME=? and SPASS=?",(uname,upass))
            data=cur.fetchone()
            if data:
                session['isLogged']=True
                session['DID']=data["DID"]
                session['SNAME']=data["SNAME"]
                session['SID']=data["SID"]
                flash('Login Successfully','success')
                return redirect('staff_home')
            else:
                flash('Invalid Login. Enter Correct Login Details','danger')
            cur.close()
    return render_template("index.html")
#Admin - home
@app.route("/home")
@is_logged_in
def home():
    return render_template("home.html")
    
#Admin - department details
@app.route("/department",methods=['GET','POST'])
@is_logged_in
def department():
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    if request.method=='POST':
        dname=request.form['dname']
        dcate=request.form['dcate']
        cur.execute("insert into department (DNAME,DCATE) values (?,?)",(dname,dcate))
        con.commit()
        flash("Department Added","info")
    cur.execute("select * from department")
    data=cur.fetchall()
    return render_template("department.html",data=data)
 
#Admin - department details edit
@app.route("/department_edit/<string:id>",methods=['GET','POST'])
@is_logged_in
def department_edit(id):
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    if request.method=='POST':
        dname=request.form['dname']
        dcate=request.form['dcate']
        cur.execute("update department  set DNAME=?,DCATE=? where DID=?",(dname,dcate,id))
        con.commit()
        flash("Department Updated","info")
    cur.execute("select * from department where did=?",(id,))
    data=cur.fetchone() 
    datas=["UG","PG"]
    return render_template("department_edit.html",data=data,datas=datas)
      
#Admin - delete department details
@app.route("/department_delete/<string:id>",methods=['GET','POST'])
@is_logged_in
def department_delete(id):
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("delete from department where DID=?",(id,))
    con.commit()
    flash("Department Deleted","danger")
    return redirect(url_for("department"))

#Admin - staff details
@app.route("/staff",methods=['GET','POST'])
@is_logged_in
def staff():
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    if request.method=='POST':
        did=request.form['did']
        sname=request.form['sname']
        spass=request.form['spass']
        year=request.form['year']
        cur.execute("insert into staff (DID,SNAME,SPASS,SYEAR) values (?,?,?,?)",(did,sname,spass,year))
        con.commit()
        flash("Staff Added","info")
        
    cur.execute("select * from department")
    data={"department":cur.fetchall()}
    
    cur.execute("select * from staff s inner join department d on s.DID=d.DID")
    data.update({"staff":cur.fetchall()})
    return render_template("staff.html",data=data)
 
#Admin - staff details
@app.route("/staff_edit/<string:sid>",methods=['GET','POST'])
@is_logged_in
def staff_edit(sid):
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    if request.method=='POST':
        did=request.form['did']
        sname=request.form['sname']
        spass=request.form['spass']
        year=request.form['year']
        cur.execute("update staff set DID=?,SNAME=?,SPASS=?,SYEAR=? where SID=?",(did,sname,spass,year,sid))
        con.commit()
        flash("Staff Updated","info")
        
    cur.execute("select * from department")
    data={"department":cur.fetchall()}
    
    cur.execute("select * from staff where SID=?",(sid,))
    info=cur.fetchone()
    return render_template("staff_edit.html",data=data,info=info)
 
#Admin - staffClass
@app.route("/staffClass",methods=['GET','POST'])
@is_logged_in
def staffClass():
    data={}
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from staff s inner join department d on s.DID=d.DID")
    data.update({"staff":cur.fetchall()})
    return render_template("staffClass.html",data=data)
 
#Admin - staff_class_assign
@app.route("/staff_class_assign/<string:sid>",methods=['GET','POST'])
@is_logged_in
def staff_class_assign(sid):
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    if request.method=='POST':
        did=request.form['did']
        year=request.form['year']
        cur.execute("INSERT into staff_class (SID,DID,YEAR) values (?,?,?)",(sid,did,year))
        con.commit()
        flash("Added Successfully","info")
        
    cur.execute("select * from department")
    data={"department":cur.fetchall()}
    
    cur.execute("select * from staff_class c inner join  department d on c.DID=d.DID where c.SID=?",(sid,))
    data.update({"records":cur.fetchall()})
    
    cur.execute("select * from staff s inner join department d on s.DID=d.DID where s.SID=?",(sid,))
    info=cur.fetchone()
    return render_template("staff_class_assign.html",data=data,info=info)
 
#Admin - staff Class assign details
@app.route("/staff_class_assign_del/<string:id>/<string:sid>",methods=['GET','POST'])
@is_logged_in
def staff_class_assign_del(id,sid):
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("delete from staff_class where ID=?",(id,))
    con.commit()
    flash("Assingment Deleted","danger")
    return redirect(url_for("staff_class_assign",sid=sid))
    
    
#Admin - delete staff details
@app.route("/staff_delete/<string:id>",methods=['GET','POST'])
@is_logged_in
def staff_delete(id):
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("delete from staff where SID=?",(id,))
    con.commit()
    flash("Staff Deleted","danger")
    return redirect(url_for("staff"))
 
#Admin -  Student View
@app.route("/student",methods=['GET','POST'])
@is_logged_in
def student():
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    data={}
    cur.execute("select * from student s inner join department d on s.DID=d.DID")
    data.update({"student":cur.fetchall()})
    return render_template("student.html",data=data)

#Admin - student Add
@app.route("/add_student",methods=['GET','POST'])
@is_logged_in
def add_student():
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from department")
    data={"department":cur.fetchall()}
    return render_template("add_student.html",data=data)

#Admin - student Edit
@app.route("/student_edit/<string:id>",methods=['GET','POST'])
@is_logged_in
def student_edit(id):
    if request.method=='POST':
        con=sql.connect("db.db")
        con.row_factory=sql.Row
        cur=con.cursor()
        did=request.form['did']
        name=request.form['name']
        rollno=request.form['rollno']
        year=request.form['year']
        sem=request.form['sem']
        cur.execute("update student set DID=?,NAME=?,ROLLNO=?,YEAR=?,SEM=? where ID=?",(did,name,rollno,year,sem,id))
        con.commit()
        flash("Details Updated","info")
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from department")
    data={"department":cur.fetchall()}
    cur.execute("select * from student where ID=?",(id,))
    data.update({"info":cur.fetchone()})
    return render_template("student_edit.html",data=data)
    
#Admin - delete student details
@app.route("/student_delete/<string:id>",methods=['GET','POST'])
@is_logged_in
def student_delete(id):
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("delete from student where ID=?",(id,))
    con.commit()
    flash("Student Deleted","danger")
    return redirect(url_for("student"))

#Admin - Report Daily Attendance
@app.route("/report_daily_attend_admin",methods=['GET','POST'])
@is_logged_in
def report_daily_attend_admin():
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    data={}
    if request.method=='POST':
        did=request.form['did']
        year=request.form['year']
        sem=request.form['sem']
        adate=request.form['adate']
        #adate=datetime.strptime(adate,"%d-%m-%Y").strftime("%Y-%m-%d")
        adate=date_user_to_db(adate)
        cur.execute("select * from attendance a inner join student s on a.ROLLNO=s.ROLLNO where a.YEAR=? and a.SEM=? and s.DID=? group by a.ROLLNO order by s.ROLLNO",(year,sem,did))
        data.update({"students":cur.fetchall()})
        data.update({"attendance":{}})
        for row in data["students"]:
            attend=[]
            for hour in range(1,7):
                cur.execute("select * from attendance where ADATE=? and ROLLNO=? and HOUR=?",(adate,row["ROLLNO"],hour))
                res=cur.fetchone()
                if res:
                    attend.append(res["ASTATUS"])
                else:
                    attend.append("")
            data.update({row["ROLLNO"]:attend})
    cur.execute("select * from department")
    data.update({"department":cur.fetchall()})
    print(data)
    date=datetime.today().strftime('%d-%m-%Y')
    return render_template("report_daily_attend_admin.html",data=data,date=date)

#Staff - Daily Attendance
@app.route("/report_single_stud_attend_admin",methods=['GET','POST'])
@is_logged_in
def report_single_stud_attend_admin():
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    data={}
    datas=""
    if request.method=='POST':
        year=request.form['year']
        sem=request.form['sem']
        rollno=request.form['rollno']
        cur.execute("select * from attendance where YEAR=? and SEM=? and ROLLNO=? group by ADATE",(year,sem,rollno))
        data.update({"students":cur.fetchall()})
        
        #Attendance Percentage Calc Variables
        total=0
        present=0
        absent=0
        for row in data["students"]:
            attend=[]
            status=1
            total+=1
            for hour in range(1,7):
                #Attendance Percentage Calc 1
                cur.execute("select * from attendance where ADATE=? and ROLLNO=? and HOUR=?",(row["ADATE"],row["ROLLNO"],hour))
                res=cur.fetchone()
                if res:
                    attend.append(res["ASTATUS"])
                    if(res["ASTATUS"]=="Absent"):
                        status=0
                else:
                    attend.append("")
                
            #Attendance Percentage Calc 2
            if status==1:
                present+=1
            else:
                absent+=1
            data.update({row["AID"]:attend})
      
        per=round((present/total)*100,2)
        datas=[total,present,absent,per]
    return render_template("report_single_stud_attend_admin.html",data=data,datas=datas)
    
#Staff Home
@app.route('/staff_home',methods=['GET','POST'])
def staff_home():
    data={}
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    if request.method=='POST':
        id=request.form['id']
        cur.execute("select * from staff_class  where ID=?",(id,))
        res=cur.fetchone()
        did=res["DID"]
        year=res["YEAR"]
        date=request.form['date']
        hour=request.form['hour']
        return redirect(url_for("staff_attend",hour=hour,date=date,id=id))
    cur.execute("select * from staff_class c inner join  department d on c.DID=d.DID where c.SID=?",(session['SID'],))
    data.update({"department":cur.fetchall()})
    return render_template("staff_home.html",data=data)
    
#Staff Attendance
@app.route('/staff_attend/<string:hour>/<string:date>/<string:id>',methods=['GET','POST'])
def staff_attend(hour,date,id):
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    cur.execute("select * from staff_class c inner join department d on c.DID=d.DID where ID=?",(id,))
    res=cur.fetchone()
    did=res["DID"]
    year=res["YEAR"]
    data={"hour":hour,"date":date,"dname":res["DNAME"],"year":res["YEAR"],"id":id,"did":did}
    return render_template("staff_attend.html",data=data)

#Staff - Compelete Attendance
@app.route("/complete_attend/<string:did>/<string:year>/<string:hour>/<string:date>",methods=['GET','POST'])
@is_logged_in
def complete_attend(did,year,hour,date):
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    day=date_user_to_db(date)
    cur.execute("select * from student where DID=? and YEAR=? and ROLLNO not in (select ROLLNO from attendance where ADATE=? and HOUR=?)",(did,year,str(day),hour))
    data=cur.fetchall()
    for row in data:
        print(row)
        cur.execute("insert into attendance (ROLLNO,ADATE,HOUR,YEAR,SEM,ASTATUS) values (?,?,?,?,?,?)",(row["ROLLNO"],day,hour,row["YEAR"],row["SEM"],'Absent'))
        con.commit()
    flash("Attendance Updated","info")
    return redirect(url_for("staff_home"))   
    
#Staff - Report Daily Attendance
@app.route("/report_daily_attend",methods=['GET','POST'])
@is_logged_in
def report_daily_attend():
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    data={}
    if request.method=='POST':
        id=request.form['did']
        cur.execute("select * from staff_class  where ID=?",(id,))
        res=cur.fetchone()
        did=res["DID"]
        year=res["YEAR"]
        sem=request.form['sem']
        adate=request.form['adate']
        #adate=datetime.strptime(adate,"%d-%m-%Y").strftime("%Y-%m-%d")
        adate=date_user_to_db(adate)
        cur.execute("select * from attendance a inner join student s on a.ROLLNO=s.ROLLNO where a.YEAR=? and a.SEM=? and s.DID=? group by a.ROLLNO order by s.ROLLNO",(year,sem,did))
        data.update({"students":cur.fetchall()})
        data.update({"attendance":{}})
        for row in data["students"]:
            attend=[]
            for hour in range(1,7):
                cur.execute("select * from attendance where ADATE=? and ROLLNO=? and HOUR=?",(adate,row["ROLLNO"],hour))
                res=cur.fetchone()
                if res:
                    attend.append(res["ASTATUS"])
                else:
                    attend.append("")
            data.update({row["ROLLNO"]:attend})
    cur.execute("select * from staff_class c inner join  department d on c.DID=d.DID where c.SID=?",(session['SID'],))
    data.update({"department":cur.fetchall()})
    print(data)
    date=datetime.today().strftime('%d-%m-%Y')
    return render_template("report_daily_attend.html",data=data,date=date)

#Staff - Daily Attendance
@app.route("/report_single_stud_attend",methods=['GET','POST'])
@is_logged_in
def report_single_stud_attend():
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
    data={}
    datas=""
    if request.method=='POST':
        year=request.form['year']
        sem=request.form['sem']
        rollno=request.form['rollno']
        cur.execute("select * from attendance where YEAR=? and SEM=? and ROLLNO=? group by ADATE",(year,sem,rollno))
        data.update({"students":cur.fetchall()})
        
        #Attendance Percentage Calc Variables
        total=0
        present=0
        absent=0
        for row in data["students"]:
            attend=[]
            status=1
            total+=1
            for hour in range(1,7):
                #Attendance Percentage Calc 1
                cur.execute("select * from attendance where ADATE=? and ROLLNO=? and HOUR=?",(row["ADATE"],row["ROLLNO"],hour))
                res=cur.fetchone()
                if res:
                    attend.append(res["ASTATUS"])
                    if(res["ASTATUS"]=="Absent"):
                        status=0
                else:
                    attend.append("")
                
            #Attendance Percentage Calc 2
            if status==1:
                present+=1
            else:
                absent+=1
            data.update({row["AID"]:attend})
      
        per=round((present/total)*100,2)
        datas=[total,present,absent,per]
    return render_template("report_single_stud_attend.html",data=data,datas=datas)
    

 
#Staff
@app.route("/logout")
def logout():
	session.clear()
	flash('Logout Successfully','success')
	return redirect("index")
    
@app.route("/add_details")
def add_details():
    return render_template("add_details.html")
 

#studentPhotoUpdate
cap=cv2.VideoCapture(0) 
@app.route("/studentPhotoUpdate",methods=['GET','POST'])
def studentPhotoUpdate():
    if request.method=='POST':
        con=sql.connect("db.db")
        con.row_factory=sql.Row
        cur=con.cursor()
        id=request.form['id']
        rollno=request.form['rollno']
        photo=rollno+".jpg"
        cur.execute("update student set PHOTO=? where ID=?",(photo,id))
        con.commit()
        success,img=cap.read()    
        imgS=cv2.resize(img,(0,0),None,0.25,0.25)
        filename = 'static/img/'+photo
        cv2.imwrite(filename, imgS)
        return 'Student Photo Updated Successfully'
    return 'Failed Try Again!!!'
 
#add student to db 
cap=cv2.VideoCapture(0) 
@app.route("/takescreenshot",methods=['GET','POST'])
def takescreenshot():
    if request.method=='POST':
        con=sql.connect("db.db")
        con.row_factory=sql.Row
        cur=con.cursor()
        did=request.form['did']
        name=request.form['name']
        rollno=request.form['rollno']
        year=request.form['year']
        sem=request.form['sem']
        photo=rollno+".jpg"
        cur.execute("insert into student (DID,NAME,ROLLNO,YEAR,PHOTO,SEM) values (?,?,?,?,?,?)",(did,name,rollno,year,photo,sem))
        con.commit()
        success,img=cap.read()    
        imgS=cv2.resize(img,(0,0),None,0.25,0.25)
        filename = 'static/img/'+photo
        cv2.imwrite(filename, imgS)
        flash("Student Added Successfully","info")
        return 'Student Added Successfully'
    return 'Failed Try Again!!!'

def video_stream():  
    while True:
        success,img=cap.read()
        imgS=cv2.resize(img,(0,0),None,0.25,0.25)
        imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)
        faceCurFrame=face_recognition.face_locations(imgS)
        for faceLoc in faceCurFrame:
            y1,x2,y2,x1=faceLoc
            y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1c,y1),(x2,y2),(0,255,0),2)
        ret, jpeg = cv2.imencode('.jpg', img)
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(),mimetype='multipart/x-mixed-replace; boundary=frame')
    
@app.route('/matching')
def matching():
    return render_template("matching.html")
    
def faceEncodings(images):
    encodeList=[]
    for img in images:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        if type(face_recognition.face_encodings(img)) is list:
            if len(face_recognition.face_encodings(img))>0:
                encode=face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
    return encodeList

#add attendance to database
def markAttendance(rollno,hour,date):
    con=sql.connect("db.db")
    con.row_factory=sql.Row
    cur=con.cursor()
   
    day = date_user_to_db(date)
    cur.execute("select * from student where ROLLNO=?",(rollno,))
    row=cur.fetchone()
    
    astatus="Present"
   
    cur.execute("select * from attendance where ROLLNO=? and ADATE=? and HOUR=?",(rollno,day,hour))
    data=cur.fetchone()
    if data:
        pass
    else:
        cur.execute("insert into attendance (ROLLNO,ADATE,HOUR,YEAR,SEM,ASTATUS) values (?,?,?,?,?,?)",(rollno,day,hour,row["YEAR"],row["SEM"],astatus))
        con.commit()
    return "Added"

#face matching attendance    
def genmatch(hour,date):
    path='static/img'
    images=[]
    classNames=[]
    myList=os.listdir(path)
    for cl in myList:
        curImg=cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    encodeListKnown=faceEncodings(images)    
    isRun=True
    while isRun:
        success,img=cap.read()
        imgS=cv2.resize(img,(0,0),None,0.25,0.25)
        imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)
        faceCurFrame=face_recognition.face_locations(imgS)
        encodesCurFrame=face_recognition.face_encodings(imgS,faceCurFrame)
        for encodeFace,faceLoc in zip(encodesCurFrame,faceCurFrame):
            matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis=face_recognition.face_distance(encodeListKnown,encodeFace)
            name=""
            status=""
            if(min(faceDis)<0.5):
                matchIndex=np.argmin(faceDis)
                # print(faceDis)
                if matches[matchIndex]:
                    name =classNames[matchIndex]
                    status=markAttendance(name,hour,date)
                    isRun=False
            y1,x2,y2,x1=faceLoc
            y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            
            cv2.putText(img,f'{name} {status}',(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
        ret, jpeg = cv2.imencode('.jpg', img)
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
 
@app.route('/video_match/<string:hour>/<string:date>',methods=['GET','POST'])
def video_match(hour,date):
    return Response(genmatch(hour,date),mimetype='multipart/x-mixed-replace; boundary=frame')


    
if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug = True)