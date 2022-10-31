
    # Name: Zhiyi Zhu
    # Student ID: 1152455


from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import mysql.connector
import connect
import uuid
import datetime
import time
from flask import session

dbconn=None
app=Flask(__name__,
          static_folder="static", 
          static_url_path="/static")   
                               



# set global time and Date
CurrentTime=datetime.datetime(2022,10,28,17,0,0)
CurrentDate=CurrentTime.date()

#set secret_key for session 
app.secret_key="1234567"

def getCursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=connect.dbuser, \
        password=connect.dbpass, host=connect.dbhost, \
        database=connect.dbname, autocommit=True)
        dbconn = connection.cursor()
        return dbconn
    if dbconn != None:
        connection.close()
        connection = mysql.connector.connect(user=connect.dbuser, \
        password=connect.dbpass, host=connect.dbhost, \
        database=connect.dbname, autocommit=True)
        dbconn = connection.cursor()
        return dbconn

#Public system main page
@app.route("/")
def HomePage():
    # This try - except statement is for user login info storage(session)
    # to prevent error page because of losing session info.  
    # I put this statement in nearly every page(function) so that if losing session data
    # when user is using the web.They will be redirected to Homepage or Login page for re-login.  
    try:   
        session["loggedFirstname"]
    except KeyError:
            session["loggedFirstname"]=""
            return render_template("HomePage.html")
    else:
            loggedFirstname=session["loggedFirstname"]
            return render_template("HomePage.html",
                                loggedFirstname=loggedFirstname)


#Public system Sign in page
@app.route("/signin")
def sign():     
    return render_template("signin.html")


#Public system Register page 
@app.route("/register")
def register():
    return render_template("register.html")


# route and function for register info validation 
@app.route("/register/checkvalid",methods=["POST"])
def register_checkvalid():
    #register info submited to this page and process
    #get user input info
    firstname=request.form["firstname"]
    lastname=request.form["lastname"]
    userID=request.form["username"]
    phone=request.form["phone"]
    passport=request.form["passport"]
    DOB=request.form["DOB"]
    
    #check if user register info existed in database or not.
    #get each user email info from database and put them in a list for later use.
    cur=getCursor()
    cur.execute("select emailaddress from passenger")
    db_emails=cur.fetchall()
    db_emails_list=[]
    for x in db_emails:
        for j in x:
            db_emails_list.append(j)
    #if user register account already exist.Promt them to sign in.
    error_message="Invalid input.Account existed.Please sign in if you aleady have an account."
    if userID in db_emails_list:
        return render_template("register.html",error_message=error_message)
    #insert new user info into database
    elif userID not in db_emails_list:
        cur.execute("""insert into passenger(FirstName,LastName,EmailAddress,PhoneNumber,PassportNumber,DateOfBirth)  
                       values(%s,%s,%s,%s,%s,%s)""",(firstname,lastname,userID,phone,passport,DOB))
        success_message="Successfully registed!"
        return render_template("register.html",success_message=success_message)
        
        
#route and function for log out .If user send log out request.Session data will be cleared. 
@app.route("/logout")
def logout():
    logoutStatus=request.args.get("logoutStatus")
    if logoutStatus=="logout":
        session["username"]=""
        session["loggedID"]=""
        session["loggedFirstname"]=""

        return render_template("HomePage.html"
                               )
                           

#Public system user page.
@app.route("/mypage",methods=["POST"])
def mypage():
    try:   
        session["loggedFirstname"]
    except KeyError:
            session["loggedFirstname"]=""
            return redirect("/signin")
    else:
        username=request.form["username"]
        print("username:",username)
        # username=request.args.get("username","")
        #sign in page info will be sent to this page and process to successfully login to personal account system.
        #get each user email info from database and put them in a list for later use.
        cur=getCursor()
        cur.execute("select EmailAddress from passenger")
        db_emails=cur.fetchall()
        db_emails_list=[]
        for x in db_emails:
            for j in x:
                db_emails_list.append(j)

        if username in db_emails_list:
            # user successfully logged in the syetem if their email is in the db email list
            # get logged user info and pass the info into session variable
            # since the email can be edited.SO we need the passenger id in the session variable
            cur=getCursor()
            cur.execute("select * from passenger where EmailAddress=%s",(username,))
            db_logged_userInfo=cur.fetchall()
            logged_userID=db_logged_userInfo[0][0]
            loggedFirstname=db_logged_userInfo[0][1]
            session["username"]=username
            session["loggedID"]=logged_userID
            session["loggedFirstname"]=loggedFirstname
            
            return render_template("mypage.html",
                                loggedFirstname=loggedFirstname,
                                username=username
                                )
        elif username not in db_emails_list:
            error_message="Not a valid account.Creat a new account if you don't have one."
            return render_template("signin.html",error_message=error_message)
        

#Public sysyem user detail page.   
@app.route("/mydetails")
def display_origi_details():
    try:   
        session["loggedFirstname"]
    except KeyError:
            session["loggedFirstname"]=""
            return redirect("/signin")
    else:
        username=session["username"]
        loggedFirstname=session["loggedFirstname"]
        #get logged user email info
        logged_userID=session["loggedID"]
        cur=getCursor()
        cur.execute("select * from passenger where PassengerID=%s",(logged_userID,))
        dbcols=[desc[0] for desc in cur.description]
        dbresult=cur.fetchall()
        
        return render_template("mydetails.html",
                            dbcols=dbcols,
                            dbresult=dbresult,
                            loggedFirstname=loggedFirstname,
                                username=username)
    
 
# route for user detail edit page.To get user original detail data and display.    
@app.route("/editdetails")
def mydetails():
    try:   
        session["loggedFirstname"]
    except KeyError:
            session["loggedFirstname"]=""
            return redirect("/signin")
    else:
        #get logged userID
        logged_userID=session["loggedID"]
        loggedFirstname=session["loggedFirstname"]
        cur=getCursor()
        cur.execute("select * from passenger where PassengerID=%s",(logged_userID,))
        column_names=[desc[0] for desc in cur.description]
        select_result=cur.fetchall()
        #get all the original logged user info and put the value in the edit page box.
        firstname=select_result[0][1]
        lastname=select_result[0][2]
        username=select_result[0][3]
        phone=select_result[0][4]
        passport=select_result[0][5]
        DOB=select_result[0][6]
        
        return render_template("editdetails.html",
                            firstname=firstname,
                                lastname=lastname,
                                username=username,
                                phone=phone,
                                passport=passport,
                                DOB=DOB,
                                loggedFirstname=loggedFirstname,
                            )
                
                
#route and function for processing detail editing.                
@app.route("/editdetails/process",methods=["POST"])
def editdetails():
    #get user edit personal details info.
    firstname=request.form["firstname"]
    lastname=request.form["lastname"]
    userID=request.form["username"]
    phone=request.form["phone"]
    passport=request.form["passport"]
    DOB=request.form["DOB"]
    #get the original username(before edit).In case the new email user input is invalid(already used by others).
    username=session["username"]
    #insert new user info into database
    #get logged passenger ID
    logged_userID=session["loggedID"]

    print(logged_userID)
    
    cur=getCursor()
    cur.execute("""update passenger 
                set FirstName=%s,LastName=%s,EmailAddress=%s,PhoneNumber=%s,PassportNumber=%s,DateOfBirth=%s
                where PassengerID=%s;""",(firstname,lastname,userID,phone,passport,DOB,logged_userID))

    return redirect("/mydetails")


    
#Public system Arrival and Depature Flight shcedules page   
@app.route("/ArrDep")
def ArrDep():
    try:   
        session["loggedFirstname"]
    except KeyError:
            session["loggedFirstname"]=""
            return redirect("/ArrDep")
    else:
             loggedFirstname=session["loggedFirstname"]
             cur=getCursor()
             cur.execute("""
                         SELECT AirportCode,concat(AirportName,'(',AirportCode,')') 
                         FROM airport order by concat(AirportName,'(',AirportCode,')') 
                         """)
             select_result_airprot=cur.fetchall()
             return render_template("ArrDep.html",
                                dbresult_airport=select_result_airprot,
                                loggedFirstname=loggedFirstname,
                                )
            
     

#To filter user choice and return related data.
@app.route("/ArrDep/process")
def match():
    try:   
        session["loggedFirstname"]
    except KeyError:
            session["loggedFirstname"]=""
            return redirect("/signin")
    else:
        loggedFirstname=session["loggedFirstname"]
        airport=request.args.get("airport","")
        cur=getCursor()
        # Arrivals Form
        cur.execute("""
                    select f.FlightNum as "Flight",f.FlightDate as "Date",a.AirportName as "From",f.ArrTime as "Sch. Arrival",f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status"
                    from flight f 
                    left join route r
                    on f.flightnum=r.flightnum
                    left join airport a 
                    on a.airportcode=r.depcode
                    where r.arrcode=%s
                    and flightdate between subdate(%s,interval 2 day) and adddate(%s,interval 5 day)
                    order by flightdate
                    """,(airport,CurrentDate,CurrentDate))
        column_names_Arr=[desc[0] for desc in cur.description]
        select_result_Arr=cur.fetchall()
        # Departures Form
        cur.execute("""
                    select f.FlightNum as "Flight",f.FlightDate as "Date",a.AirportName as "To",f.DepTime as "Sch. Departure",f.DepEstAct as "Est/Act Departure",f.FlightStatus as "Status"
                    from flight f 
                    left join route r
                    on f.flightnum=r.flightnum
                    left join airport a 
                    on a.airportcode=r.arrcode
                    where r.depcode=%s and flightdate between subdate(%s,interval 2 day) and adddate(%s,interval 5 day)
                    order by flightdate
                    """,(airport,CurrentDate,CurrentDate))
        select_result_Dep=cur.fetchall()
        column_names_Dep=[desc[0] for desc in cur.description]
        

        cur.execute("SELECT AirportCode,concat(AirportName,'(',AirportCode,')') FROM airport order by concat(AirportName,'(',AirportCode,')')")    
        select_result_airprot=cur.fetchall()
        
        return render_template("ArrDep.html",
                            airport_selected=airport,
                            dbresult_Arr=select_result_Arr,
                            dbresult_Dep=select_result_Dep,
                            dbcols_Arr=column_names_Arr,
                            dbcols_Dep=column_names_Dep,
                            dbresult_airport=select_result_airprot,
                            loggedFirstname=loggedFirstname,
                            )


#Public system user booking management page                     
@app.route("/mybooking")
def mybooking():
    try:   
        session["loggedFirstname"]
    except KeyError:
            session["loggedFirstname"]=""
            return redirect("/signin")
    else:
        #get logged user info from session
        loggedID=session["loggedID"]
        username=session["username"]
        loggedFirstname=session["loggedFirstname"]
        cur=getCursor()
        cur.execute("""
                    select f.FlightID as "Flight",p.FirstName as "First Name",p.LastName as "Last Name",f.FlightNum as "Flight",f.FlightDate as "Date",airdep.AirportName as"From",
                    airarr.airportname as "To",f.Duration,f.deptime as "Sch. Departure",f.arrtime as "Sch. Arrival",f.depestact as "Est/Act Departure",f.arrestact as "Est/Act Arrival",f.FlightStatus as "Status"
                    from passengerFlight pf 
                    left join flight f on f.flightID=pf.flightID
                    left join passenger p on p.passengerID=pf.passengerID
                    left join route r on f.flightnum=r.flightnum
                    left join airport airdep on airdep.airportcode=r.depcode
                    left join airport airarr on airarr.airportcode=r.arrcode
                    where p.PassengerID=%s
                    order by flightdate
                    """,(loggedID,))
        column_names=[desc[0] for desc in cur.description]
        select_result=cur.fetchall()
        return render_template("mybooking.html",
                            dbcols=column_names,
                            dbresult=select_result,
                            loggedFirstname=loggedFirstname,
                                username=username)
        
        
#Public system user management page -cancel function
@app.route("/cancelbookings")
def cancel():
    # get logged user info from session
    #get the flight id of the flight need to be canceled
    flightID_tobecanceled=request.args.get("flightID_tobecanceled")
    #get logged userID(passengerID) from session
    loggedID=session["loggedID"]
    cur=getCursor()
    cur.execute("delete from passengerFlight where FlightID=%s and PassengerID=%s",(flightID_tobecanceled,loggedID))
    return redirect("/mybooking")
    

#Public system flight booking page     
@app.route("/bookaflight")
def bookaflight():
    try:   
        session["loggedFirstname"]
    except KeyError:
            session["username"]=""
            session["loggedID"]=""
            session["loggedFirstname"]=""
            return redirect("/bookaflight")
    else:
    #when user send logout request.session value will be set to ""        
        loggedFirstname=session["loggedFirstname"]
        if loggedFirstname=="":
            return render_template("noticeSignin.html")
        else:
            cur=getCursor()
            cur.execute("SELECT AirportName,concat(AirportName,'(',AirportCode,')') FROM airport order by concat(AirportName,'(',AirportCode,')')")
            select_result=cur.fetchall() 
            return render_template("bookaflight.html",
                                dbresult_airport_list=select_result,
                                loggedFirstname=loggedFirstname,
                                    CurrentDate=CurrentDate,
                                )


#route and function for filtering user choice and return related data.    
@app.route("/bookaflight/process")
def BAFprocess():
    try:   
        session["loggedFirstname"]
    except KeyError:
            session["loggedFirstname"]=""
            return redirect("/signin")
    else:
        #get logged user info from session
        loggedID=session["loggedID"]
        username=session["username"]
        loggedFirstname=session["loggedFirstname"]
        DepAirportSelected=request.args.get("departureAirport")
        print("DepAirportSelected",DepAirportSelected)
        dateSelected=request.args.get("dateSelected")
        #store the user choice for later use
        session["DepAirportSelected"]=DepAirportSelected
        session["dateSelected"]=dateSelected
        
    
        #Only future flights are shown.
        if dateSelected==str(CurrentDate):
            dateSelectedoriginal=dateSelected
            dateSelected=CurrentTime
            #get flight schedules for future 7 days of the selected airport and date from database
            cur=getCursor()
            cur.execute("""
                        select  f.FlightID as "Flight ID",f.FlightNum as "Flight",f.FlightDate as "Date",airdep.AirportName as"From",
                        airarr.AirportName as "To",f.Duration,f.DepTime as "Sch. Departure",f.ArrTime as "Sch. Arrival",f.DepEstAct as "Est/Act Departure",
                        f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status",
                        (craft.Seating-ifnull(fbook.SeatBooked,0)) as "Available Seats"
                        from flight f
                        left join (SELECT pf.FlightID,count(FlightID) as SeatBooked from passengerFlight pf 
                        group by flightid) as fbook on f.FlightID=fbook.FlightID
                        left join route r on f.FlightNum=r.FlightNum
                        left join airport airdep on airdep.AirportCode=r.DepCode
                        left join airport airarr on airarr.AirportCode=r.ArrCode
                        left join aircraft craft on craft.RegMark=f.Aircraft
                        where airdep.AirportName =%s and
                        FlightDate between %s and adddate(%s,interval 7 day)
                        order by f.FlightDate
                        """,(DepAirportSelected,dateSelected,dateSelected))
            column_names=[desc[0] for desc in cur.description]
            select_result=cur.fetchall()
            #Inorder to pass variable pass into input value as date value instead of time format 
            dateSelected=dateSelectedoriginal
        else:
            cur=getCursor()
            cur.execute("""
                        select  f.FlightID as "Flight ID",f.FlightNum as "Flight",f.FlightDate as "Date",airdep.AirportName as"From",
                        airarr.AirportName as "To",f.Duration,f.DepTime as "Sch. Departure",f.ArrTime as "Sch. Arrival",f.DepEstAct as "Est/Act Departure",
                        f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status",
                        (craft.Seating-ifnull(fbook.SeatBooked,0)) as "Available Seats"
                        from flight f
                        left join (SELECT pf.FlightID,count(flightID) as SeatBooked from passengerFlight pf 
                        group by FlightID) as fbook on f.FlightID=fbook.FlightID
                        left join route r on f.FlightNum=r.FlightNum
                        left join airport airdep on airdep.AirportCode=r.DepCode
                        left join airport airarr on airarr.AirportCode=r.ArrCode
                        left join aircraft craft on craft.RegMark=f.Aircraft
                        where airdep.AirportName =%s and
                        FlightDate between %s and adddate(%s,interval 7 day)
                        order by f.FlightDate
                        """,(DepAirportSelected,dateSelected,dateSelected))
            column_names=[desc[0] for desc in cur.description]
            select_result=cur.fetchall()
        #need to get the departure airport list from database again for the drop down list info not missing.
        cur=getCursor()
        cur.execute("SELECT AirportName,concat(AirportName,'(',AirportCode,')') FROM airport order by concat(AirportName,'(',AirportCode,')') ")
        select_result1=cur.fetchall() 
        disabled="disabled"
        return render_template("bookaflight.html",
                            dbcols=column_names,
                            dbresult=select_result,
                            DepAirportSelected=DepAirportSelected,
                            dateSelected=dateSelected,
                            loggedFirstname=loggedFirstname,
                                username=username,
                                loggedID=loggedID,
                                dbresult_airport_list=select_result1,
                                disabled=disabled,
                                CurrentDate=CurrentDate
                            )
        
        
#Public system flight booking function .Return avalible filghts        
@app.route("/bookbutton")
def bookbutton():
    try:   
        session["loggedFirstname"]
    except KeyError:
            session["loggedFirstname"]=""
            return redirect("/signin")
    else:
        loggedID=session["loggedID"]
        username=session["username"]
        loggedFirstname=session["loggedFirstname"]
        #    Check each flight availability
        #    Get all the passenger-flight book info from database.
        #    Put all the passenger-flight info combination in a list for later use.    
        #the flightid_seatnum string need to be converted to list type first 
        #from the flightid_seatnum list we can extra the flightid and seat available number for each flight
        flightID_seatNum=request.args.get("flightID_seatNum")
        flightID_seatNum=flightID_seatNum.split(",")
        flightID_tobebooked=flightID_seatNum[0]
        seatAvailableNum=int(flightID_seatNum[1])
        disabled="disabled"
        #get logged user info from session
        loggedID=session["loggedID"]
        cur=getCursor()
        cur.execute("""
                    SELECT concat(FlightID,"-",PassengerID) as "primary key" FROM passengerFlight;
                    """)
        select_result_flightid_passengerid=cur.fetchall() 
        flightBookedList=[]
        for x in select_result_flightid_passengerid:
            for z in x:
                flightBookedList.append(z)
                
        # 2) if flights already booked by the logged user.'Book' button will show a disabled 'Booked' button.        
        flightID_loggedID_tobebooked=f"{flightID_tobebooked}-{loggedID}"
        if flightID_loggedID_tobebooked in flightBookedList:
            system_message="You've already booked this Flight!"
        # 3) if the flight not be booked by the user before.Book the user in the flight.
        elif flightID_loggedID_tobebooked not in flightBookedList:
                cur=getCursor()
                cur.execute("""
                        insert into passengerFlight (FlightID,PassengerID) 
                        values(%s,%s)
                        """,(flightID_tobebooked,loggedID))
                system_message="""Successfully Booked in! 
                                Manage your booking in 'My Booking'."""
        cur=getCursor()
        cur.execute("""
                    select f.FlightID as "Flight ID",p.FirstName as "First Name",p.LastName as "Last Name",f.FlightNum as "Flight",f.FlightDate as "Date",airdep.AirportName as"From",
                    airarr.AirportName as "To",f.Duration,f.DepTime as "Sch. Departure",f.ArrTime as "Sch. Arrival",f.DepEstAct as "Est/Act Departure",f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status"
                    from passengerFlight pf 
                    left join flight f on f.FlightID=pf.FlightID
                    left join passenger p on p.PassengerID=pf.PassengerID
                    left join route r on f.FlightNum=r.FlightNum
                    left join airport airdep on airdep.AirportCode=r.DepCode
                    left join airport airarr on airarr.AirportCode=r.ArrCode
                    where p.PassengerID=%s
                    order by FlightDate
                    """,(loggedID,))
        column_names=[desc[0] for desc in cur.description]
        select_result=cur.fetchall()
        return render_template("mybooking.html",
                            dbcols=column_names,
                            dbresult=select_result,
                            loggedFirstname=loggedFirstname,
                                username=username,
                                system_message=system_message,
                                disabled=disabled
                            )
        



#Management system main page
@app.route("/admin")
def admin():
    try:   
            session["logged_staffName"]
            session["logged_staffIsManager"]
    except KeyError:
            return render_template("admin.html")
    else: 
            #when user send logout request.session value will be set to ""       
        if session["logged_staffName"] =="" and session["logged_staffIsManager"]=="":
            return render_template("admin.html")
        else:
            logged_staffName=session["logged_staffName"]
            logged_staffIsManager=session["logged_staffIsManager"]
            return render_template("admin.html",
                                    logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager)


#Management system sign in page
@app.route("/admin/signin")
def adminSignin():
    #get staff name for log in system
    cur=getCursor()
    cur.execute("SELECT StaffID,FirstName,LastName,EmailAddress,PhoneNumber,PassportNumber,DateOfBirth,IsManager FROM staff;")
    select_result=cur.fetchall() 
    #get if there is logged user info

    return render_template("adminSignin.html",
                           dbresult=select_result,
                           )
    
  
#Management system log out function.When user send log out request.Session user data  will be cleared. 
@app.route("/admin/staffpage/logout")
def logout_admin():
    logoutStatus_staff=request.args.get("logoutStatus_staff")
    if logoutStatus_staff=="logout":
        session["logged_staffID"]=""
        session["logged_staffName"]=""
        session["logoutvisible"]=""
        login_nav="Log in"
        print("afterclicklockout",session["logged_staffID"])
        return redirect("/admin")
    
    
##Management system  staff page    
@app.route("/admin/staffpage",methods=["POST"])
def staffpage():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        #get logged staff info and put that in session for later use
        logged_staffID=request.form["staffID"]
        cur=getCursor()
        cur.execute("SELECT StaffID,FirstName,LastName,EmailAddress,PhoneNumber,PassportNumber,DateOfBirth,IsManager FROM staff where StaffID=%s",(logged_staffID,))
        select_result=cur.fetchall() 
        logged_staff_info_list=[]
        for result in select_result:
            for entry in result:
                logged_staff_info_list.append(entry)
        session["logged_staffID"]=logged_staff_info_list[0]
        session["logged_staffName"]=logged_staff_info_list[1]+" "+logged_staff_info_list[2]
        session["logged_staffIsManager"]=logged_staff_info_list[-1]
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        return render_template("staffpage.html",
                            logged_staffName=logged_staffName,
                            logged_staffID=logged_staffID,
                            logged_staffIsManager=logged_staffIsManager)

    

##Management system  staff details page    
@app.route("/admin/staffpage/staffdetails")
def stafftable():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        #get logged staff info 
        logged_staffID=session["logged_staffID"]
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        cur=getCursor()
        cur.execute("SELECT StaffID,FirstName,LastName,EmailAddress,PhoneNumber,PassportNumber,DateOfBirth,IsManager FROM staff where StaffID=%s",(logged_staffID,))
        dbcols=[desc[0] for desc in cur.description]
        select_result=cur.fetchall() 
        return render_template("staffdetails.html",
                            dbcols=dbcols,
                            dbresult=select_result, 
                            logged_staffID=logged_staffID,
                            logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager
                                )
    
##Management system  passenger list page            
@app.route("/admin/staffpage/passenger")   
def passengerlist():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        cur=getCursor()
        cur.execute("SELECT DISTINCT LastName FROM passenger order by LastName")
        select_result_passengerLastname=cur.fetchall() 
        cur.execute("""
                    SELECT PassengerID as "Passenger ID",concat(LastName," ",FirstName) as "Passenger Name" ,EmailAddress as "Email",
                    PhoneNumber as "Phone",PassportNumber as "Passport",DateOfBirth as "DOB",Loyaltytier as "Loyalty Tier"
                    FROM passenger
                    order by concat(LastName," ",FirstName)
                    ;
                    """)
        dbcols=[desc[0] for desc in cur.description]
        select_result=cur.fetchall() 

        return render_template("passenger.html",
                            dbresult_passengerLastname=select_result_passengerLastname,
                            dbcols=dbcols,
                            dbresult=select_result,
                            logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager
    )


##Management system  funtion for passneger list user choice filer.
@app.route("/admin/staffpage/passenger/process")
def passengerProcess():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        #get user input passenger lastname
        LastnameInput=request.args.get("passengerName","")
        if LastnameInput=="":
            return redirect("/admin/staffpage/passenger")
        else:
            LastnameInput_sql=f"{LastnameInput}%"
            #extract user-input-lastname related info from database
            cur=getCursor()
            cur.execute("""SELECT PassengerID as "Passenger ID",concat(LastName," ",FirstName) as "Passenger Name" ,EmailAddress as "Email",
                            PhoneNumber as "Phone",PassportNumber as "Passport",DateOfBirth as "DOB",LoyaltyTier as "Loyalty Tier"
                            FROM passenger
                            where LastName LIKE %s;""",(LastnameInput_sql,))
            select_result_lastnamefilter=cur.fetchall() 
            dbcols_filter=[desc[0] for desc in cur.description]
            #To make the input datalist work normal.need to put values in.
            cur=getCursor()
            cur.execute("SELECT  DISTINCT LastName FROM passenger order by LastName")
            select_result_passengerLastname=cur.fetchall() 
            dbcols=[desc[0] for desc in cur.description]
            return render_template("passenger.html",
                                dbcols_filter=dbcols_filter,
                                dbresult_filter=select_result_lastnamefilter,
                                dbcols=dbcols,
                                dbresult_passengerLastname=select_result_passengerLastname,
                                LastnameInput=LastnameInput,
                                logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager)
            
            
#show original passenger details
@app.route("/admin/staffpage/passenger/edit")
def passengerDetailsEdit():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        #get the passengerID for the passenger need to be edited
        passengerIDSelected=request.args.get("passengerIDeach")
        flightIDEach=request.args.get("flightIDEach")
        session["passengerIDSelected"]=passengerIDSelected
        #get the passenger details from database
        cur=getCursor()
        cur.execute("select PassengerID,FirstName,LastName,EmailAddress,PhoneNumber,PassportNumber,DateOfBirth,LoyaltyTier from passenger where PassengerID=%s",(passengerIDSelected,))
        column_names=[desc[0] for desc in cur.description]
        select_result=cur.fetchall()
        list=[]
        for x in select_result:
            for z in x:
                list.append(z)
        #get all the original logged user info and put the value in the edit page box.
        firstname=list[1]
        lastname=list[2]
        username=list[3]
        phone=list[4]
        passport=list[5]
        DOB=list[6]
        
        
        return render_template("editdetailsAdmin.html",
                            firstname=firstname,
                                lastname=lastname,
                                username=username,
                                phone=phone,
                                passport=passport,
                                DOB=DOB,
                                passengerIDSelected=passengerIDSelected,
                                flightIDEach=flightIDEach,
                                logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager

                            )
    

##Management system  function for processing edit details
@app.route("/admin/staffpage/passenger/edit/process")
def passengerDetailsEdit_admin():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        # post Methods.
        #get required  passenger info from html
        # passengerIDSelected=request.form["ID"]
        # firstname=request.form["firstname"]
        # lastname=request.form["lastname"]
        # userID=request.form["username"]
        # phone=request.form["phone"]
        # passport=request.form["passport"]
        # DOB=request.form["DOB"]
        # flightIDEach=request.args.get("flightIDEach")
        passengerIDSelected=session["passengerIDSelected"]
        # passengerIDSelected=request.args.get("ID")
        firstname=request.args.get("firstname")
        lastname=request.args.get("lastname")
        userID=request.args.get("username")
        phone=request.args.get("phone")
        passport=request.args.get("passport")
        DOB=request.args.get("DOB")
        flightIDEach=request.args.get("flightIDEach")
        cur=getCursor()
        cur.execute("""update passenger 
                    set FirstName=%s,LastName=%s,EmailAddress=%s,PhoneNumber=%s,PassportNumber=%s,DateOfBirth=%s
                    where PassengerID=%s;""",(firstname,lastname,userID,phone,passport,DOB,passengerIDSelected))
        success_message="Successfully updated!"
        #after updated,the passenger page will show the updated selected passenger details.
        # The “backButton” is a link to go back to previous passenger list page. 
        #get the passengerID for the passenger selected
        cur=getCursor()
        #in order to bring user back to passenger page with a "successfully changed" notice
        cur.execute("""
                    SELECT PassengerID as "Passenger ID",concat(LastName," ",FirstName) as "Passenger Name" ,EmailAddress as "Email",
                    PhoneNumber as "Phone",PassportNumber as "Passport",DateOfBirth as "DOB",LoyaltyTier  as "Loyal Tytier "
                    FROM passenger
                    where  PassengerID=%s
                    """,(passengerIDSelected,))
        dbcols=[desc[0] for desc in cur.description]
        select_result=cur.fetchall() 
        return render_template("passengerEach.html",
                            dbcols=dbcols,
                            dbresult=select_result,
                                success_message= success_message,
                                flightIDEach=flightIDEach,
                                logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager)


##Management system each passenger page    
@app.route("/admin/staffpage/passenger/each")
def eachPassenger():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]

        #get the passengerID for the passenger selected
        #this is on passenger/each page,click view booking in this page will be for the same passenger
        #put the passenger ID in session for view the booking process.
        passengerIDeach=request.args.get("selectedPassengerID")
        session["passengerIDeach"]=passengerIDeach
        flightIDEach=request.args.get("flightIDEach","None")
        print("pasengereachpage,flightIDeach:",flightIDEach)
        print(type(flightIDEach))
        cur=getCursor()
        #in order to bring user back to passenger page with a "successfully changed" notice
        cur.execute("""
                    SELECT PassengerID as "Passenger ID",concat(LastName," ",FirstName) as "Passenger Name" ,EmailAddress as "Email",
                    PhoneNumber as "Phone",PassportNumber as "Passport",DateOfBirth as "DOB",LoyaltyTier as "Loyalty Tier"
                    FROM passenger
                    where  PassengerID=%s
                    """,(passengerIDeach,))
        dbcols=[desc[0] for desc in cur.description]
        select_result=cur.fetchall() 
        #get the selected info from database and put and in session     
        list=[]
        for x in select_result:
            for z in x:
                list.append(z)
        print(list)
        print(type(list))
        if list!=[]:
            session["passengerName"]=list[1]
        return render_template("passengerEach.html",
                            dbcols=dbcols,
                            dbresult=select_result,
                            flightIDEach=flightIDEach,
                            logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager

                            )
 
 
##Management system  passenger booking page    
@app.route("/admin/staffpage/passenger/booking")
def PassengerBooking():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]

        #第一页用的
        passengerIDeach=request.args.get("selectedPassengerID")
        flightIDEach=request.args.get("flightIDEach")

        passengerName=request.args.get("passengerName")
        logged_staffName=session["logged_staffName"]
        #extract related flight booking info from database for the selected passenger from the passenger/each page
        cur=getCursor()
        cur.execute("""
                    select f.FlightID as "Flight ID",f.FlightNum as "Flight",f.FlightDate as "Date",airdep.AirportName as"From",
                    airarr.AirportName as "To",f.Duration,f.DepTime as "Sch. Departure",f.ArrTime as "Sch. Arrival",f.DepEstAct as "Est/Act Departure",f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status"
                    from passenger p
                    left join passengerFlight pf on p.PassengerID=pf.PassengerID
                    left join flight f on f.FlightID=pf.FlightID
                    left join route r on f.FlightNum=r.FlightNum
                    left join airport airdep on airdep.AirportCode=r.DepCode
                    left join airport airarr on airarr.AirportCode=r.ArrCode
                    where p.PassengerID=%s
                    order by FlightDate,DepTime
                    """,(passengerIDeach,))
        dbcols=[desc[0] for desc in cur.description]
        select_result=cur.fetchall()  
        print("select_result",select_result[0][0])
        print(type(select_result[0][0]))
        return render_template("passengerbooking.html",
                            dbcols=dbcols,
                            dbresult=select_result,
                            passengerName=passengerName,
                            passengerIDeach=passengerIDeach,
                            flightIDEach=flightIDEach,
                            logged_staffName=logged_staffName,
                            logged_staffIsManager=logged_staffIsManager
                            )
        
        
##Management system function for add flights for passengers        
@app.route("/admin/staffpage/passenger/booking/addPassengerflightProcess")
def addPassengerFlightsProcess():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        #for reschedule flight for selected passenger.To reschedule flights,Firstlt book in new availabe flights.
        # Secondly,cancel the original flights. 

        originalFlightID=request.args.get("originalFlightID")
        print("originalFlightID:", originalFlightID)
        flightIDEach=request.args.get("flightIDEach")
        print("flightideach:",flightIDEach)
        
        #for add new flights for selected passenger
        passengerName=request.args.get("passengerName")
        print("inaddprocess",passengerName)
        passengerIDeach=request.args.get("passengerIDeach")
        flightIDtobeadded=request.args.get("flightID")
        print("passengerIDeach",passengerIDeach)
        print("flightIDtobeadded",flightIDtobeadded)
        #insert passenger id and flight id into passengerFlight table to add flight for the selected passenger.
        cur=getCursor()
        cur.execute("""
                    SELECT concat(FlightID,"-",PassengerID) as "primary key" FROM passengerFlight;
                    """)
        
        select_result_flightid_passengerid=cur.fetchall() 
        flightBookedList=[]
        for x in select_result_flightid_passengerid:
            for z in x:
                flightBookedList.append(z)
                
        # 2) if flights already booked by the logged user.'Book' button will show a disabled 'Booked' button.        
        flightID_loggedID_tobebooked=f"{flightIDtobeadded}-{passengerIDeach}"
        print("flightID_loggedID_tobebooked",flightID_loggedID_tobebooked)
        print(bool(flightID_loggedID_tobebooked in flightBookedList))
        if flightID_loggedID_tobebooked in flightBookedList:
            error_message="You've already booked this Flight!"
            success_message="None"
            print("already booked")
        # 3) if the flight not be booked by the user before.Book the user in the flight.
        else:
            print("enter else")
            cur=getCursor()
            cur.execute("""
                    insert into passengerFlight (FlightID,PassengerID) 
                    values(%s,%s)
                    """,(flightIDtobeadded,passengerIDeach))
                    #get the user choice from session
            print("successfully booked")
            success_message="""Successfully Booked in! """
            error_message="None"
            if originalFlightID!='None':
                cur.execute("delete from passengerFlight where FlightID=%s and PassengerID=%s",(originalFlightID,passengerIDeach))
                print("delete part done!")
        cur=getCursor()
        cur.execute("""
                select f.FlightID as "Flight ID",f.FlightNum as "Flight",f.FlightDate as "Date",airdep.AirportName as"From",
                airarr.AirportName as "To",f.Duration,f.DepTime as "Sch. Departure",f.ArrTime as "Sch. Arrival",f.DepEstAct as "Est/Act Departure",f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status"
                from passenger p
                left join passengerFlight pf on p.PassengerID=pf.PassengerID
                left join flight f on f.FlightID=pf.FlightID
                left join route r on f.FlightNum=r.FlightNum
                left join airport airdep on airdep.AirportCode=r.DepCode
                left join airport airarr on airarr.AirportCode=r.ArrCode
                where p.PassengerID=%s
                order by FlightDate,DepTime
                """,(passengerIDeach,))
        dbcols=[desc[0] for desc in cur.description]
        select_result=cur.fetchall()     
        return render_template("passengerbooking.html",
                                dbcols=dbcols,
                            dbresult=select_result,
                            passengerName=passengerName,
                            passengerIDeach=passengerIDeach,
                            success_message=success_message,
                            error_message=error_message,
                                logged_staffName=logged_staffName,
                            logged_staffIsManager=logged_staffIsManager,
                            flightIDEach=flightIDEach,
                            )
        
  
##Management system  flight cancel function    
@app.route("/admin/staffpage/passenger/booking/cancel")
def passengerBookingCancel():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        passenger_flightID_tobecanceled=request.args.get("flightID")
        passengerIDeach=request.args.get("passengerIDeach")
        passengerName=request.args.get("passengerName")
        flightIDEach=request.args.get("flightIDEach","None")
        #extract related flight booking info from database for the selected passenger from the passenger/each page
        cur=getCursor()
        cur.execute("delete from passengerFlight where FlightID=%s and PassengerID=%s",(passenger_flightID_tobecanceled,passengerIDeach))

        cur=getCursor()
        cur.execute("""
                    select f.FlightID as "Flight ID",f.FlightNum as "Flight",f.FlightDate as "Date",airdep.AirportName as"From",
                    airarr.AirportName as "To",f.Duration,f.DepTime as "Sch. Departure",f.ArrTime as "Sch. Arrival",f.DepEstAct as "Est/Act Departure",f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status"
                    from passenger p
                    left join passengerFlight pf on p.PassengerID=pf.PassengerID
                    left join flight f on f.FlightID=pf.FlightID
                    left join route r on f.FlightNum=r.FlightNum
                    left join airport airdep on airdep.AirportCode=r.DepCode
                    left join airport airarr on airarr.AirportCode=r.ArrCode
                    where p.PassengerID=%s
                    order by FlightDate,DepTime
                    """,(passengerIDeach,))
        dbcols=[desc[0] for desc in cur.description]
        select_result=cur.fetchall()
            
        return render_template("passengerbooking.html",
                            dbcols=dbcols,
                            dbresult=select_result,
                            passengerName=passengerName,
                            passengerIDeach=passengerIDeach,
                            flightIDEach=flightIDEach,logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager                 
                            )


##Management system flight list page
@app.route("/admin/staffpage/flights")
def flightsAdmin():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        #for reschedule flightsfor passengers from passenger magnagement page.
        originalFlightID=request.args.get("originalFlightID")
        passengerName=request.args.get("passengerName")
        #for add flights for passengers from passenger magnagement page.
        passengerIDeach=request.args.get("passengerIDeach")
        disabled="disabled"
        
        flightIDEach=request.args.get("flightIDEach","None")
        
        DepAirport=request.args.get("DepAirport","")
        ArrAirport=request.args.get("ArrAirport","")
        startDate=request.args.get("dateStart",CurrentTime)
        delta=datetime.timedelta(days=7)
        setEndDate=CurrentTime+delta
        
        endDate=request.args.get("dateEnd",setEndDate)
        
        #if users dont choose date,the date value will be sent back empty string 
        #if users didnt select  both start date  and end date.The default start date is default current time
        if startDate=="" and endDate=="":
            startDate=CurrentTime
            endDate=setEndDate
        #if users didnt select end date only select the start date.The default end date is 7 days after the selected start date.
        elif startDate!="":
            if endDate=="":
                startDate=datetime.datetime.strptime(startDate,('%Y-%m-%d'))
                endDate=startDate+delta
        #If users didnt select start date only select end date,the default start date is default Current Time
        elif endDate!="":
            if startDate=="":
                endDate=datetime.datetime.strptime(endDate,('%Y-%m-%d'))
                if endDate>CurrentTime: 
                    startDate=CurrentTime
                elif endDate<CurrentTime:
                    startDate=""
        
        DepAirport_filter=f"{DepAirport}%"
        ArrAirport_filter=f"{ArrAirport}%"
        
        cur=getCursor()
        cur.execute("SELECT airportname,concat(AirportName,'(',AirportCode,')') FROM airport")
        select_result_airportList=cur.fetchall()
        
        cur=getCursor()
        cur.execute("""
                    select  f.FlightID as "Flight ID",f.FlightNum as "Flight",f.FlightDate as "Date",airdep.AirportName as"From",
                    airarr.AirportName as "To",f.Duration,f.DepTime as "Sch. DeparTure",f.ArrTime as "Sch. Arrival",f.DepEstAct as "Est/Act Departure",
                    f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status",f.Aircraft,ifnull(fbook.SeatBooked,0) as "Seats Booked",
                    (craft.Seating-ifnull(fbook.SeatBooked,0)) as "Available Seats"
                    from flight f
                    left join (SELECT pf.FlightID,count(FlightID) as SeatBooked from passengerFlight pf 
                    group by flightid) as fbook on f.FlightID=fbook.FlightID
                    left join route r on f.FlightNum=r.FlightNum
                    left join airport airdep on airdep.AirportCode=r.DepCode
                    left join airport airarr on airarr.AirportCode=r.ArrCode
                    left join aircraft craft on craft.RegMark=f.Aircraft
                    where 
                    airdep.AirportName  LIKE %s and
                    airarr.AirportName LIKE %s and
                    FlightDate between %s and %s
                    order by f.FlightDate,DepTime,airdep.AirportName

                    """,(DepAirport_filter,ArrAirport_filter,startDate,endDate))
        dbcols=[desc[0] for desc in cur.description]
        select_result=cur.fetchall()
        # datetime format cannot be remembered by the date input box.
        if type(startDate)==datetime.datetime:
            startDate=str(startDate.date())   
        if type(endDate)==datetime.datetime:
            endDate=str(endDate.date())
        return render_template("flightsAdmin.html",
                            dbresult_airport_list=select_result_airportList,
                            dbcols_filter=dbcols,
                            dbresult_filter=select_result,
                            DepAirport=DepAirport,
                            ArrAirport=ArrAirport,
                            startDate=startDate,
                            endDate=endDate,
                            passengerIDeach=passengerIDeach,
                            disabled=disabled,
                            originalFlightID=originalFlightID,
                            logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager,
                                passengerName=passengerName,
                                flightIDEach=flightIDEach
                                                )

   
#Management system  each flight page   
@app.route("/admin/staffpage/flights/each")
def eachfight(): 
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else: 
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        print("logged_staffName",logged_staffName)
        #managers can edit all details of a flight, while other staff can only edit the status and the estimated/actual times.
        logged_staffIsManager=session["logged_staffIsManager"]    
        if logged_staffIsManager ==0:
            disabled="disabled"
        elif logged_staffIsManager==1:
            disabled=""  
        flightIDEach=request.args.get("flightIDEach")
        
        cur=getCursor()
        cur.execute("""
                select  f.FlightNum as "Flight",f.FlightDate as "Date",airdep.AirportName as"From",
                    airarr.AirportName as "To",f.Duration,f.DepTime as "Sch. Departure",f.ArrTime as "Sch. Arrival",f.DepEstAct as "Est/Act Departure",
                    f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status",f.Aircraft,craft.Seating as "Seat Capasity",ifnull(fbook.SeatBooked,0) as "Seat Booked",
                    (craft.Seating-ifnull(fbook.SeatBooked,0)) as "Available Seats"
                    from flight f
                    left join (SELECT pf.FlightID,count(FlightID) as SeatBooked from passengerFlight pf 
                    group by FlightID) as fbook on f.FlightID=fbook.FlightID
                    left join route r on f.FlightNum=r.FlightNum
                    left join airport airdep on airdep.AirportCode=r.DepCode
                    left join airport airarr on airarr.AirportCode=r.ArrCode
                    left join aircraft craft on craft.RegMark=f.AirCraft
                    where f.FlightID=%s
                    order by f.FlightDate,DepTime,airdep.AirportName
                    """,(flightIDEach,))
        dbcols=[desc[0] for desc in cur.description]
        select_result=cur.fetchall()
        #passenger list form
        cur=getCursor()
        cur.execute("""
                    select pf.PassengerID as  "Passenger ID",concat(LastName," ",FirstName) as "Passenger Name" ,p.EmailAddress as "Email",p.PhoneNumber as "Phone",
                    p.PassportNumber as "Passport",p.DateOfBirth as "DOB",p.LoyaltyTier as "Loyalty Tier"
                    from flight f 
                    left join passengerFlight pf on pf.FlightID=f.FlightID
                    left join passenger p on p.PassengerID=pf.PassengerID
                    where pf.FlightID=%s
                    order by concat(LastName," ",FirstName)

                    """,(flightIDEach,))
        dbcols_Plist=[desc[0] for desc in cur.description]
        dbresult_Plist=cur.fetchall()
        return render_template("flightEach.html",
                            dbcols=dbcols,
                            dbresult=select_result,
                            flightIDEach=flightIDEach,
                                dbcols_Plist=dbcols_Plist,
                            dbresult_Plist=dbresult_Plist,
                            disabled=disabled,
                            logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager                
                            )
        

#Management system add individual flight page
@app.route("/admin/staffpage/addAflight")
def addAflight():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffName=session["logged_staffName"]
        logged_staffIsManager=session["logged_staffIsManager"]
        if logged_staffIsManager ==0:
            return "Only Manager can add flights."
        elif logged_staffIsManager==1:
            cur=getCursor()
            cur.execute("""
                    select FlightNum,concat(FlightNum," (",DepCode,"-",ArrCode,")") from route
                        order by FlightNum
                        """)
            select_result_flightnum=cur.fetchall()
            session["select_result_flightnum"]=select_result_flightnum
            cur=getCursor()
            cur.execute("""
                        SELECT DISTINCT Regmark from aircraft
                        order by RegMark
                        """)
            select_result_regmark=cur.fetchall()
            session['select_result_regmark']=select_result_regmark
            return render_template("addAflight.html",
                                dbresult_flightnum=select_result_flightnum,
                                    dbresult_regmark=select_result_regmark,
                                    CurrentDate=CurrentDate,
                                    logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager
    )
   
   
#Management system funtion for adding a flight .      
@app.route("/admin/staffpage/addAflight/process")
def addAflightProcess():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffIsManager=session["logged_staffIsManager"]
        logged_staffName=session["logged_staffName"]
        flightNum=request.args.get("flightNum")
        flightDate=request.args.get("flightDate")
        scheduledDepTime=request.args.get("scheduledDepTime")
        scheduledArrTime=request.args.get("scheduledArrTime")
        aircraft=request.args.get("aircraft")
        flightStatus=request.args.get("flightStatus")
        
        #get the corresponding week num for inserting new flight.
        # This task set period '2022-10-24' to '2022-10-31' as week1 which is the 43rd week of 2022.
        flightDate=datetime.datetime.strptime(flightDate,('%Y-%m-%d'))
        weekNum=int(flightDate.strftime("%W"))-42
        print(weekNum)
        #Calculate duration time
        scheduledDepTime1=datetime.datetime.strptime(scheduledDepTime,('%H:%M'))
        scheduledArrTime1=datetime.datetime.strptime(scheduledArrTime,('%H:%M'))
        duration=scheduledArrTime1-scheduledDepTime1
        print(duration)
        print(type(duration))
        cur=getCursor()
        cur.execute("""
                insert into flight (FlightNum,WeekNum,FlightDate,Duration,DepTime,ArrTime,DepEstAct,ArrEstAct,FlightStatus,Aircraft)
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);

                    """,(flightNum,weekNum,flightDate,duration,scheduledDepTime,scheduledArrTime,scheduledDepTime,scheduledArrTime,flightStatus,aircraft))
        cur.execute("SELECT FlightID FROM flight;")
        select_result_flightid=cur.fetchall()
        #get flight id from database and put them in a list and find the maxest flight id
        list=[]
        for x in select_result_flightid:
            for z in x:
                list.append(z)
        flightIDadded=max(list)
        
        cur.execute("""
                    select  f.FlightID as "Flight ID",f.FlightNum as "Flight",f.FlightDate as "Date",f.WeekNum as "Week Num",airdep.AirportName as"From",
                    airarr.AirportName as "To",f.Duration,f.DepTime as "Sch. Departure",f.ArrTime as "Sch. Arrival",f.DepEstAct as "Est/Act Departure",
                    f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status",f.Aircraft,ifnull(fbook.SeatBooked,0) as "Seat Booked",
                    (craft.Seating-ifnull(fbook.SeatBooked,0)) as "Available Seats"
                    from flight f
                    left join (SELECT pf.FlightID,count(FlightID) as SeatBooked from passengerFlight pf 
                    group by FlightID) as fbook on f.FlightID=fbook.FlightID
                    left join route r on f.FlightNum=r.FlightNum
                    left join airport airdep on airdep.AirportCode=r.DepCode
                    left join airport airarr on airarr.AirportCode=r.ArrCode
                    left join aircraft craft on craft.RegMark=f.Aircraft
                    where f.FlightID=%s
                    order by f.FlightDate,DepTime,airdep.AirportName
                    """,(flightIDadded,))
        select_result_flightid_added=cur.fetchall()
        dbcols_flightid_added=[desc[0] for desc in cur.description]
        
        #in order to get the input boxes worked.Need to put needed variables in
        select_result_flightnum=session["select_result_flightnum"]
        select_result_regmark=session['select_result_regmark']
        
        return render_template("addAflight.html",
                            dbresult_flightid_added=select_result_flightid_added,
                            dbcols_flightid_added=dbcols_flightid_added,
                            dbresult_flightnum=select_result_flightnum,
                                    dbresult_regmark=select_result_regmark,
                                    logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager)
        
    
##Management system add flights page    
@app.route("/admin/staffpage/addflights")
def addflights():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffName=session["logged_staffName"]
        logged_staffIsManager=session["logged_staffIsManager"]
        if logged_staffIsManager ==0:
            return "Only Manager can add flights."
        elif logged_staffIsManager==1:
            cur=getCursor()
            cur.execute(" SELECT distinct WeekNum FROM flight;")
            select_result_weeknum=cur.fetchall()
            #get all week num from database and put them in a list and find the maxest week num
            list=[]
            for x in select_result_weeknum:
                for z in x:
                    list.append(z)
            weekNumMax=max(list)
            #for the next week flight schedules.
            weeknumMaxNextweek=int(weekNumMax)+1
            #display the latest week flight schedules
            cur.execute("""
                    select  f.FlightID as "Flight ID",f.FlightNum as "Flight",f.FlightDate as "Date",f.WeekNum as "Week Num",airdep.AirportName as"From",
                    airarr.AirportName as "To",f.Duration,f.DepTime as "Sch. Departure",f.ArrTime as "Sch. Arrival",f.DepEstAct as "Est/Act Departure",
                    f.ArrEstAct as "Est/Act Arrival",f.FlightStatus as "Status",f.Aircraft,ifnull(fbook.SeatBooked,0) as "Seat Booked",
                    (craft.Seating-ifnull(fbook.SeatBooked,0)) as "Available Seats"
                    from flight f
                    left join (SELECT pf.FlightID,count(FlightID) as SeatBooked from passengerFlight pf 
                    group by FlightID) as fbook on f.FlightID=fbook.FlightID
                    left join route r on f.FlightNum=r.FlightNum
                    left join airport airdep on airdep.AirportCode=r.DepCode
                    left join airport airarr on airarr.AirportCode=r.ArrCode
                    left join aircraft craft on craft.RegMark=f.Aircraft
                    where f.WeekNum=%s
                    order by f.FlightDate,DepTime,airdep.AirportName
                    """,(weekNumMax,))
            select_result_flightsByWeek=cur.fetchall()
            dbcols_flights_flightsByWeek=[desc[0] for desc in cur.description]
            return render_template("addflights.html",
                            dbresult_flightsByWeek= select_result_flightsByWeek,
                            dbcols_flightsByWeek=dbcols_flights_flightsByWeek,
                                weekNumMax=weekNumMax,
                                weeknumMaxNextweek=weeknumMaxNextweek,
                                logged_staffName=logged_staffName,
                                logged_staffIsManager=logged_staffIsManager)
 
 
##Management system add next week flight page            
@app.route("/admin/staffpage/addflights/nextweek")
def nextweekFlights():
    cur=getCursor()
    cur.execute("""
                INSERT INTO flight(FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft)
                SELECT FlightNum, WeekNum+1, date_add(FlightDate, interval 7 day), DepTime, ArrTime, Duration, DepTime, ArrTime, 'On time', Aircraft
                FROM flight
                WHERE WeekNum = (SELECT MAX(WeekNum) FROM flight);
                """)
    return redirect("/admin/staffpage/addflights")


#Management system  for edit flight details 
@app.route("/admin/staffpage/editflights")
def editflights():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        logged_staffName=session["logged_staffName"]
        #managers can edit all details of a flight, while other staff can only edit the status and the 
        # estimated/actual times.
        logged_staffIsManager=session["logged_staffIsManager"]
        print(logged_staffIsManager)
        if logged_staffIsManager ==0:
            disabled="disabled"
        elif logged_staffIsManager==1:
            disabled=""
        
        flightIDEach=request.args.get("flightIDEach")
        cur=getCursor()
        cur.execute("SELECT FlightID,FlightNum,WeekNum,FlightDate,DepTime,ArrTime,Duration,DepEstAct,ArrEstAct,FlightStatus,Aircraft FROM flight where FlightID=%s",(flightIDEach,))
        select_result_flightinfo=cur.fetchall()
        
        #put all related info in list
        list=[]
        for x in select_result_flightinfo:
            for z in x:
                list.append(z) 
        print("list:",list)   
        flightNum=list[1]
        flightDate=list[3]
        #To get all format right
        scheduledDepTime=str(list[4])
        if  scheduledDepTime!='None': 
            scheduledDepTime=time.strptime(scheduledDepTime,"%H:%M:%S")
            scheduledDepTime=time.strftime("%H:%M:%S",scheduledDepTime)
        scheduledArrTime=str(list[5])
        if scheduledArrTime!='None':
            scheduledArrTime=time.strptime(scheduledArrTime,"%H:%M:%S")
            scheduledArrTime=time.strftime("%H:%M:%S",scheduledArrTime)
        actdeptime=str(list[7])
        if actdeptime!='None':
            actdeptime=time.strptime(actdeptime,"%H:%M:%S")
            actdeptime=time.strftime("%H:%M:%S",actdeptime)
        actarrtime=str(list[8])  
        if actarrtime!='None' :   
            actarrtime=time.strptime(actarrtime,"%H:%M:%S")
            actarrtime=time.strftime("%H:%M:%S",actarrtime)
        flightStatus=list[9]
        aircraft=list[10]
        
        #convert time format
        cur=getCursor()
        cur.execute("SELECT FlightStatus FROM status order by FlightStatus;")
        select_result_flightstatus=cur.fetchall()
        
        cur=getCursor()
        cur.execute("""
                    select FlightNum,concat(FlightNum," (",DepCode,"-",ArrCode,")") from route
                    order by FlightNum
                    """)
        select_result_flightnum=cur.fetchall()
        session["select_result_flightnum"]=select_result_flightnum
        
        cur=getCursor()
        cur.execute("""
                    SELECT  DISTINCT RegMark from aircraft
                    order by RegMark
                    """)
        select_result_regmark=cur.fetchall()
        selected="selected"
        return render_template("editflights.html",
                            dbresult_flightstatus=select_result_flightstatus,
                                dbresult_flightnum=select_result_flightnum,
                                    dbresult_regmark=select_result_regmark,
                                    flightIDEach=flightIDEach,
                                    flightNum=flightNum,
                                    flightDate=flightDate,
                                    scheduledDepTime=scheduledDepTime,
                                    scheduledArrTime=scheduledArrTime,
                                    actdeptime=actdeptime,
                                    actarrtime=actarrtime,
                                    flightStatus=flightStatus,
                                    aircraft=aircraft,
                                    selected=selected,
                                    disabled=disabled,
                                    loggedstaffIsManager=logged_staffIsManager,
                                    logged_staffName=logged_staffName,                             
                                )
        
        
 #Management system function for processing edit flight details       
@app.route("/admin/staffpage/editflights/process")
def editflightsProcess():
    try:   
         session["logged_staffName"]
         session["logged_staffIsManager"]
    except KeyError:
            session["logged_staffName"]=""
            session["logged_staffIsManager"]=""
            return redirect("/admin/signin")
    else:
        flightIDEach=request.args.get("flightIDEach")
        flightNum=request.args.get("flightNum")
        flightDate=request.args.get("flightDate")
        scheduledDepTime=request.args.get("scheduledDepTime")
        scheduledArrTime=request.args.get("scheduledArrTime")
        actdeptime=request.args.get("actdeptime")
        actarrtime=request.args.get("actarrtime")
        fligtStatus=request.args.get("fligtStatus")
        aircraft=request.args.get("aircraft")
        
        if fligtStatus=="Cancelled":
            actdeptime=None
            actarrtime=None

        cur=getCursor()
        cur.execute("""
                    update flight set FlightNum=%s,FlightDate=%s,DepTime=%s,ArrTime=%s,
                    DepEstAct=%s,ArrEstAct=%s,FlightStatus=%s,Aircraft=%s
                    where FlightID=%s
                    """,(flightNum,flightDate,scheduledDepTime,scheduledArrTime,actdeptime,actarrtime,fligtStatus,aircraft,flightIDEach))
        return redirect(f"/admin/staffpage/flights/each?flightIDEach={flightIDEach}")


#Management system function for other staff(not manager) editing flight details
@app.route("/admin/staffpage/editflights/process/class0")
def editflightsProcessNotManager():
    flightIDEach=request.args.get("flightIDEach")
    actdeptime=request.args.get("actdeptime")
    actarrtime=request.args.get("actarrtime")
    fligtStatus=request.args.get("fligtStatus")
    
    if fligtStatus=="Cancelled":
        actdeptime=None
        actarrtime=None

    cur=getCursor()
    cur.execute("""
                update flight set DepEstAct=%s,ArrEstAct=%s,FlightStatus=%s
                where FlightID=%s
                """,(actdeptime,actarrtime,fligtStatus,flightIDEach))
    return redirect(f"/admin/staffpage/flights/each?flightIDEach={flightIDEach}")

@app.route("/admin/staffpage/editflights/cancelflights")
def cancelflights():
    flightIDEach=request.args.get("flightIDEach")
    cur=getCursor()
    cur.execute("""
               delete from flight where FlightID=%s
                """,(flightIDEach,))
    return redirect("/admin/staffpage/flights")