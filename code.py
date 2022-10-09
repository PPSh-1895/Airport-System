#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import string
import datetime
import logging
import ast
import numpy as np
import json
import matplotlib.pyplot as plt
from io import BytesIO
#Initialize the app from Flask
app = Flask(__name__)
#logger=logging.getLogger('app')
#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='HMSKagami',
                       db='project',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

def return_img_stream(img_local_path):
    """
    工具函数:
    获取本地图片流
    :param img_local_path:文件单张图片的本地绝对路径
    :return: 图片流
    """
    import base64
    img_stream = ''
    with open(img_local_path, 'rb') as img_f:
        img_stream = img_f.read()
        img_stream = base64.b64encode(img_stream).decode()
    return img_stream

#Define a route to hello function
@app.route('/')
def hello():
    return redirect(url_for('home'))

@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    usertype = request.form['usertype']

    #cursor used to send queries
    cursor = conn.cursor()
    if usertype=="customer":
        #executes query
        query = 'SELECT * FROM customer WHERE email = %s and password = %s'
        cursor.execute(query, (username, password))
    elif usertype == "airline staff":
        query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
        cursor.execute(query, (username, password))
    elif usertype=="booking agent":
        query = 'SELECT * FROM booking_agent WHERE email = %s and password = %s'
        cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
	#creates a session for the the user
	#session is a built in
        session['username'] = username
        session['usertype'] = usertype
        if usertype=="customer":
            return redirect(url_for('customer'))
        elif usertype=="booking agent":
            return redirect(url_for("bookingagent"))
        elif usertype=="airline staff":
            return redirect(url_for("airlinestaff"))
        return redirect(url_for('home'))
    else:
	#returns an error message to the html page
        error = 'Invalid username, password, or usertype'
        return render_template('login.html', error=error)
    
@app.route('/CRregister')
def CRregister():
    return render_template("customer register.html")

@app.route('/BAregister')
def BAregister():
    return render_template("booking agent register.html")

@app.route('/ASregister')
def ASregister():
    return render_template("airline staff register.html")
#Authenticates the register
@app.route('/CRregisterAuth', methods=['GET', 'POST'])
def CRregisterAuth():
    #grabs information from the forms
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    building_number=request.form['building_number']
    street=request.form['street']
    city=request.form['city']
    state=request.form['state']
    phone_number=request.form['phone_number']
    passport_number=request.form['passport_number']
    passport_expiration=request.form['passport_expiration']
    passport_country=request.form['passport_country']
    date_of_birth=request.form['date_of_birth']

    #cursor used to send queries
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
	#If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('customer register.html', error = error)
    else:
        query = 'Insert into customer values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query, (email,name,password,building_number,street,city,state,phone_number,passport_number,passport_expiration,passport_country,date_of_birth))
        conn.commit()
        cursor.close()
        return render_template('home.html')
    
@app.route('/BAregisterAuth', methods=['GET', 'POST'])
def BAregisterAuth():
    #grabs information from the forms
    booking_agent_id = request.form['booking_agent_id']
    password = request.form['password']
    email=request.form['email']

    #cursor used to send queries
    cursor = conn.cursor()
    query = 'SELECT * FROM booking_agent WHERE email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
	#If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('booking agent register.html', error = error)
    else:
        query = 'Insert into booking_agent values (%s, %s, %s)'
        cursor.execute(query, (email,password,booking_agent_id))
        conn.commit()
        cursor.close()
        return render_template('home.html')
    
@app.route('/ASregisterAuth', methods=['GET', 'POST'])
def ASregisterAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    airline_name=request.form['airline_name']
    date_of_birth=request.form['date_of_birth']
    first_name=request.form['first_name']
    last_name=request.form['last_name']

    #cursor used to send queries
    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
	#If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('airline staff register.html', error = error)
    else:
        query = 'Insert into airline_staff values(%s,%s,%s,%s,%s,%s)'
        cursor.execute(query, (username,password,first_name,last_name,date_of_birth,airline_name))
        conn.commit()
        cursor.close()
        return render_template('home.html')


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/search',methods=['GET', 'POST'])
def search():
    try:
        source_city = request.form['source city']
        destination_city = request.form['destination city']
        date = request.form['date']
    except:
        source_city=None
    try:
        arrival_date = request.form['arrival date']
    except:
        arrival_date=None
    try:
        flight_num=int(request.form['flight number'])
    except:
        flight_num=None
    try:
        departure_date = request.form['departure date']
    except:
        departure_date=None
    if flight_num==None:
        year,month,day=date.split('-')
        cursor = conn.cursor()
        query = "SELECT * FROM flight as F WHERE status='Upcoming'and extract(year from departure_time)=%s and extract(month from departure_time)=%s and extract(day from departure_time)=%s and exists (select airport_city from airport as A where F.departure_airport=A.airport_name and airport_city=%s) and exists (select airport_city from airport as B where F.arrival_airport=B.airport_name and airport_city=%s)"
        cursor.execute(query, (year,month,day,source_city,destination_city))
        data=cursor.fetchall()
        cursor.close()
        flights = data
        return render_template('search.html',flight=flights)
    else:
        if arrival_date=="" and departure_date == "":
            error = "Please enter either date or both"
            return render_template('home.html', error = error)
        elif arrival_date=="" and departure_date != "":
            year,month,day=departure_date.split('-')
            cursor = conn.cursor()
            query= "select * from flight where flight_num=%s and extract(YEAR from departure_time)=%s and extract(MONTH from departure_time)=%s and extract(DAY from departure_time)=%s"
            cursor.execute(query,(flight_num,year,month,day))
            data=cursor.fetchall()
            cursor.close()
            flights=data
            return render_template('search.html',flight=flights)
        elif departure_date == "":
            year,month,day=arrival_date.split('-')
            cursor = conn.cursor()
            query= "select * from flight where flight_num=%s and extract(YEAR from arrival_time)=%s and extract(MONTH from arrival_time)=%s and extract(DAY from arrival_time)=%s"
            cursor.execute(query,(flight_num,year,month,day))
            data=cursor.fetchall()
            cursor.close()
            flights=data
            return render_template('search.html',flight=flights)
        else:
            year1,month1,day1=arrival_date.split('-')
            year2,month2,day2=departure_date.split('-')
            cursor = conn.cursor()
            query= "select * from flight where flight_num=%s and extract(YEAR from arrival_time)=%s and extract(MONTH from arrival_time)=%s and extract(DAY from arrival_time)=%s and extract(YEAR from departure_time)=%s and extract(MONTH from departure_time)=%s and extract(DAY from departure_time)=%s"
            cursor.execute(query,(flight_num,year1,month1,day1,year2,month2,day2))
            data=cursor.fetchall()
            cursor.close()
            flights=data
            return render_template('search.html',flight=flights)
            
            
@app.route('/customer',methods=['GET', 'POST'])
def customer():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from customer where email=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        error = "Unauthorized!"
        return render_template('home.html', error = error)

    cursor.close()
    return render_template('customer user.html',username=session["username"],usertype=session["usertype"])
        
@app.route('/CRflights',methods=["POST"])
def CRflights():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from customer where email=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        error = "Unauthorized!"
        return render_template('home.html', error = error)
    
    source_city=request.form["source city"]
    destination_city=request.form["destination city"]
    date=request.form["date"]
    
    if source_city=="": ##default
        query="select * from flight natural join ticket natural join purchases where customer_email=%s and status='Upcoming'"
        cursor.execute(query,(username))
        flights=cursor.fetchall()
        return render_template("customer view my flight.html",flight=flights)
    else:
        year,month,day=date.split("-")
        query="select * from (flight natural join ticket natural join purchases) where customer_email=%s and departure_airport in (select airport_name from airport where airport_city=%s) and arrival_airport in (select airport_name from airport where airport_city=%s) and extract(year from departure_time)=%s and extract(month from departure_time)=%s and extract(day from departure_time)=%s"
        cursor.execute(query,(username,source_city,destination_city,year,month,day))
        flights=cursor.fetchall()
        return render_template("customer view my flight.html",flight=flights)
        
@app.route('/CRsearch',methods=['GET','POST'])
def CRsearch():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from customer where email=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        error = "Unauthorized!"
        return render_template('home.html', error = error)
    
    source_city=request.form['source city']
    destination_city = request.form['destination city']
    date = request.form['date']
    year,month,day=date.split('-')
    query='SELECT * FROM flight as F WHERE status="Upcoming" and extract(year from departure_time)=%s and extract(month from departure_time)=%s and extract(day from departure_time)=%s and exists (select airport_city from airport as A where F.departure_airport=A.airport_name and airport_city=%s) and exists (select airport_city from airport as B where F.arrival_airport=B.airport_name and airport_city=%s)'
    cursor.execute(query, (year,month,day,source_city,destination_city))
    data=cursor.fetchall()
    cursor.close()
    flights=data
    session["flights"]=flights
    return render_template('customer search.html',flight=flights)

@app.route('/CRbook', methods=['POST'])
def CRbook():
    try: #Auth
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from customer where email=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        error = "Unauthorized!"
        return render_template('home.html', error = error)
    
    line=request.form["ticket"]
    airline_name,flight_num=line.split(",")
    customer_email=session['username']
    query="select max(ticket_id) as maxid from ticket"
    cursor.execute(query)
    data=cursor.fetchone()
    ticket_id=data["maxid"]+1 #increment the ticket_id
    query= "insert into ticket values(%s,%s,%s)"
    cursor.execute(query,(ticket_id,airline_name,flight_num))
    conn.commit()
    purchase_date=datetime.datetime.now().strftime("%Y-%m-%d")
    query="insert into purchases values(%s,%s,null,%s)"
    cursor.execute(query,(ticket_id,customer_email,purchase_date))
    conn.commit()
    return render_template('customer search.html',flight=session["flights"])

@app.route('/CRbarchart',methods=['GET','POST'])
def CRbarchart():
    try:
        email=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from customer where email=%s"
    cursor.execute(query,(email))
    data=cursor.fetchone()
    if (not data): #authorization
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    def x_axis_output(beginning_year,beginning_month,current_year,current_month):
        x_axis=[]
        while beginning_year!=current_year or beginning_month!=current_month:
            x_axis.append([beginning_year,beginning_month])
            if beginning_month==12:
                beginning_year+=1
                beginning_month=1
            else:
                beginning_month+=1
        x_axis.append([beginning_year,beginning_month])
        return x_axis

    month_range=request.form['time']
    if month_range=="":
        month_range=6
    else:
        month_range=int(month_range)
    current=datetime.datetime.now()
    beginning_date=(current-datetime.timedelta(days=30*month_range+month_range//2)).strftime("%Y-%m-%d")
    current_date=datetime.datetime.now().strftime("%Y-%m-%d");
    current_year,current_month,current_day=current_date.split('-')
    
    beginning_year,beginning_month,beginning_day=beginning_date.split("-")

    x=x_axis_output(int(beginning_year), int(beginning_month),int(current_year),int(current_month))
    query="drop view if exists temp_purchases"
    cursor.execute(query)
    query="create view `temp_purchases` as select ticket_id, customer_email as email, extract(year from purchase_date) as purchase_year, extract(month from purchase_date) as purchase_month from purchases where customer_email=%s and purchase_date>=%s"
    cursor.execute(query,(email,beginning_date))
    query="select sum(price) as prices,purchase_year,purchase_month from ticket natural join flight natural join temp_purchases group by purchase_year,purchase_month order by purchase_year, purchase_month asc"
    cursor.execute(query)
    data=cursor.fetchall()

    y=[]
    sum_prices=0
    y_index=0
    for i in x:
        if i[0]!=data[y_index]["purchase_year"] or i[1]!=data[y_index]["purchase_month"]:
            y.append(0)
        else:
            y.append(float(data[y_index]["prices"]))
            y_index+=1
    return render_template("customer barchart.html",total=sum(y),x=x,y=y)

@app.route('/bookingagent',methods=['GET', 'POST'])
def bookingagent():
    try:
        BAemail=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)

    query="select airline_name from booking_agent natural join booking_agent_work_for where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchall()
    if (data):
        airline_names=[]
        for i in data:
            airline_names.append(i["airline_name"])
    else:
        airline_names=""
    session["airline_name"]=airline_names
    
    #viewtop
    BAemail=session['username']
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data): #authorization
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    current_date=datetime.datetime.now()
    beginning_date1=current_date-datetime.timedelta(days=183)
    query1="select count(ticket_id) as tic_n, customer_email from purchases natural join booking_agent where email=%s and purchase_date>=%s group by customer_email order by tic_n desc"
    cursor.execute(query1,(BAemail,beginning_date1))
    data1=cursor.fetchall()
    x1=[]
    y1=[]
    for i in range(min(5,len(data1))):
        y1.append(data1[i]['tic_n'])
        x1.append(data1[i]['customer_email'])

    beginning_date2=current_date-datetime.timedelta(days=365)
    query2="select sum(price) as tot, customer_email from ((ticket left outer join flight on ticket.flight_num=flight.flight_num) left outer join purchases on ticket.ticket_id=purchases.ticket_id) left outer join booking_agent on booking_agent.booking_agent_id=purchases.booking_agent_id where email=%s and purchase_date>=%s group by customer_email order by tot desc"
    cursor.execute(query2,(BAemail,beginning_date2))
    data2=cursor.fetchall()
    x2=[]
    y2=[]
    for i in range(min(5,len(data2))):
        x2.append(data2[i]['customer_email'])
        y2.append(float(data2[i]['tot'])*0.05)
        
    cursor.close()
    return render_template("booking agent user.html",x1=x1,x2=x2,username=session["username"],usertype=session["usertype"])

@app.route('/BAflights',methods=["POST"])
def BAflights():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        error = "Unauthorized!"
        return render_template('home.html', error = error)
    
    source_city=request.form["source city"]
    destination_city=request.form["destination city"]
    date=request.form["date"]
    
    if source_city=="": ##default
        query="select * from flight natural join ticket natural join purchases natural join booking_agent where email=%s and status='Upcoming'"
        cursor.execute(query,(username))
        flights=cursor.fetchall()
        return render_template("booking agent view my flights.html",flight=flights)
    else:
        year,month,day=date.split("-")
        query="select * from (flight natural join ticket natural join purchases natural join booking_agent) where email=%s and departure_airport in (select airport_name from airport where airport_city=%s) and arrival_airport in (select airport_name from airport where airport_city=%s) and extract(year from departure_time)=%s and extract(month from departure_time)=%s and extract(day from departure_time)=%s"
        cursor.execute(query,(username,source_city,destination_city,year,month,day))
        flights=cursor.fetchall()
        return render_template("booking agent view my flights.html",flight=flights)
    
@app.route('/BAsearch',methods=['GET','POST'])
def BAsearch():
    try:
        BAemail=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data):
        error = "Unauthorized!"
        return render_template('home.html', error = error)


    source_city=request.form['source city']
    destination_city = request.form['destination city']
    date = request.form['date']
    year,month,day=date.split('-')
    query='SELECT * FROM flight as F WHERE status="Upcoming" and extract(year from departure_time)=%s and extract(month from departure_time)=%s and extract(day from departure_time)=%s and exists (select airport_city from airport as A where F.departure_airport=A.airport_name and airport_city=%s) and exists (select airport_city from airport as B where F.arrival_airport=B.airport_name and airport_city=%s)'
    cursor.execute(query, (year,month,day,source_city,destination_city))
    data=cursor.fetchall()
    cursor.close()
    flights=data
    session["flights"]=flights
    return render_template('booking agent search.html',flight=flights)

@app.route('/BAbook', methods=['POST'])
def BAbook():
    try:
        BAemail=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data): #authorization
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    customer=request.form["customer"]
    line=request.form["ticket"]
    airline_name,flight_num,airline_name=line.split(",")
    if airline_name not in session["airline_name"]:
        error="You can only book ticket of your own airline!"
        return render_template('booking agent search.html',flight=session["flights"], error=error)
    query="select max(ticket_id) as maxid from ticket"
    cursor.execute(query)
    data=cursor.fetchone()
    ticket_id=data["maxid"]+1 #increment the ticket_id
    query= "insert into ticket values(%s,%s,%s)"
    cursor.execute(query,(ticket_id,airline_name,flight_num))
    conn.commit()
    query="select booking_agent_id from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    BAid=int(cursor.fetchone()["booking_agent_id"])
    purchase_date=datetime.datetime.now().strftime("%Y-%m-%d")
    query="insert into purchases values(%s,%s,%s,%s)"
    cursor.execute(query,(ticket_id,customer,BAid,purchase_date))
    conn.commit()
    cursor.close()
    return render_template('booking agent search.html',flight=session["flights"])

@app.route('/commission',methods=['POST'])
def commission():
    try:
        BAemail=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data): #authorization
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    past_days=request.form['time']
    if past_days=="":
        past_days=30
    else:
        past_days=int(past_days)
    current_date=datetime.datetime.now()
    beginning_date=current_date-datetime.timedelta(days=past_days)
    
    query="select price from ((ticket left outer join flight on ticket.flight_num=flight.flight_num) left outer join purchases on ticket.ticket_id=purchases.ticket_id) left outer join booking_agent on booking_agent.booking_agent_id=purchases.booking_agent_id where email=%s and purchase_date>=%s"
    cursor.execute(query,(BAemail,beginning_date))
    data=cursor.fetchall()
    commissions=[]
    for i in data:
        commissions.append(float(i['price']))
    total_com=sum(commissions)*0.05
    total_tic=len(commissions)
    avg_com=total_com/total_tic
    cursor.close()
    return render_template('booking agent commission.html',time=past_days,total_commission=total_com,average_commission=avg_com,total_ticket=total_tic)
'''
@app.route('/BAbarchartticket',methods=["POST"])
def BAbarchartticket():
    try:
        BAemail=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data): #authorization
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    BAemail=session['username']
    past_date=int(request.form["date"])
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data): #authorization
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    current_date=datetime.datetime.now()
    beginning_date1=current_date-datetime.timedelta(days=past_date)
    query1="select count(ticket_id) as tic_n, customer_email from purchases natural join booking_agent where email=%s and purchase_date>=%s group by customer_email order by tic_n desc limit 5"
    cursor.execute(query1,(BAemail,beginning_date1))
    data1=cursor.fetchall()
    x1=[]
    y1=[]
    for i in range(min(5,len(data1))):
        y1.append(data1[i]['tic_n'])
        x1.append(i+1)
        
    booking_agents=[]
    for i in data1:
        booking_agents.append(i["customer_email"])
    cursor.close()
    return render_template('booking agent barchart ticket.html', x1=x1,y1=y1,booking_agents=booking_agents)
'''

@app.route('/BABticket',methods=["POST"])
def BABticket():
    try:
        BAemail=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data): #authorization
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    BAemail=session['username']
    past_date=int(request.form["date"])
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data): #authorization
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    current_date=datetime.datetime.now()
    beginning_date1=current_date-datetime.timedelta(days=past_date)
    query1="select count(ticket_id) as tic_n, customer_email from purchases natural join booking_agent where email=%s and purchase_date>=%s group by customer_email order by tic_n desc limit 5"
    cursor.execute(query1,(BAemail,beginning_date1))
    data1=cursor.fetchall()
    x1=[]
    y1=[]
    for i in range(min(5,len(data1))):
        y1.append(data1[i]['tic_n'])
        x1.append(data1[i]["customer_email"])
        
    booking_agents=[]
    for i in data1:
        booking_agents.append(i["customer_email"])
    cursor.close()
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x()+rect.get_width()/2.-0.2, 1.03*height, '%s'%float(height))
    img = BytesIO()
    plt.figure(figsize=(12, 8), dpi=100, facecolor='1.0')
    plt.title("top customer by ticket", fontsize=20)
    b=plt.bar(x1,y1)
    autolabel(b)
    plt.xlabel("customer")
    plt.ylabel("ticket bought")
    plt.savefig("image.png",format="png")
    img_path = 'image.png'
    img_stream = return_img_stream(img_path)
    return render_template('BABticket.html',image=img_stream,booking_agents=x1)

@app.route('/BABcommission',methods=["POST"])
def BABcommission():
    try:
        BAemail=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data): #authorization
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    BAemail=session['username']
    past_date=int(request.form["date"])
    cursor = conn.cursor()
    query="select * from booking_agent where email=%s"
    cursor.execute(query,(BAemail))
    data=cursor.fetchone()
    if (not data): #authorization
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    current_date=datetime.datetime.now()
    beginning_date2=current_date-datetime.timedelta(days=past_date)
    query2="select sum(price) as tot, customer_email from ((ticket left outer join flight on ticket.flight_num=flight.flight_num) left outer join purchases on ticket.ticket_id=purchases.ticket_id) left outer join booking_agent on booking_agent.booking_agent_id=purchases.booking_agent_id where email=%s and purchase_date>=%s group by customer_email order by tot desc limit 5"
    cursor.execute(query2,(BAemail,beginning_date2))
    data2=cursor.fetchall()
    x2=[]
    y2=[]
    for i in range(min(5,len(data2))):
        x2.append(data2[i]["customer_email"])
        y2.append(float(data2[i]['tot'])*0.05)
    booking_agents=[]
    for i in data2:
        booking_agents.append(i["customer_email"])
    cursor.close()
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x()+rect.get_width()/2.-0.2, 1.03*height, '%s'%float(height))
    img = BytesIO()
    plt.figure(figsize=(12, 8), dpi=100, facecolor='1.0')
    plt.title("top customer by commission", fontsize=20)
    b=plt.bar(x2,y2)
    autolabel(b)
    plt.xlabel("customer")
    plt.ylabel("commission")
    plt.savefig("image2.png",format="png")
    img_path = 'image2.png'
    img_stream = return_img_stream(img_path)
    return render_template('BABcommission.html',image=img_stream,booking_agents=x2)

@app.route('/airlinestaff',methods=['GET','POST'])
def airlinestaff():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):  
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    else:
        session["airline_name"]=data["airline_name"]
    
    query="select * from flight where status='Upcoming'and (airline_name,flight_num) in (select airline_name, flight_num from flight where airline_name in (select airline_name from airline_staff where username=%s))"
    cursor.execute(query,(username))
    data=cursor.fetchall()
    flights =data
    session["flights"]=flights

    #top5
    current_date=datetime.datetime.now()
    beginning_date=current_date-datetime.timedelta(days=365)
    query="with temp as (select sum(price) as past_year_commission, email from ticket natural join flight natural join purchases natural join booking_agent where purchase_date>=%s group by email order by past_year_commission desc) select * from temp limit 5"
    cursor.execute(query,(beginning_date))
    data=cursor.fetchall()
    top5=data
    for i in top5:
        i["past_year_commission"]=float(i["past_year_commission"])*0.05
    session["top5"]=top5
        
    #view frequent customers
    beginning_date2=current_date-datetime.timedelta(days=365)
    query="drop view if exists counter "
    cursor.execute(query)
    query="create view counter as (select count(ticket_id) as c, customer_email from purchases where purchase_date>=%s group by customer_email)"
    cursor.execute(query,(beginning_date2))
    query="select customer_email from counter where c=(select max(c) from counter)"
    cursor.execute(query)
    data=cursor.fetchone()
    customer1=data["customer_email"]
    query="drop view if exists counter"
    cursor.execute(query)
    session["customer1"]=customer1

    #top destiny
    beginning_date3=current_date-datetime.timedelta(days=91)
    query="drop view if exists top3dest "
    cursor.execute(query)
    query="create view top3dest as (select count(ticket_id) as c, airport_city from (purchases natural join ticket natural join flight) inner join airport on flight.arrival_airport=airport.airport_name where purchase_date>=%s group by airport_city order by c desc)"
    cursor.execute(query,(beginning_date3))
    query="select airport_city from top3dest limit 3"
    cursor.execute(query)
    data=cursor.fetchall()
    top3={}
    top3["last_3_month"]=[]
    for i in data:
        top3["last_3_month"].append(i["airport_city"])
    query="drop view if exists top3dest"
    cursor.execute(query)

    beginning_date3=current_date-datetime.timedelta(days=365)
    query="drop view if exists top3dest "
    cursor.execute(query)
    query="create view top3dest as (select count(ticket_id) as c, airport_city from (purchases natural join ticket natural join flight) inner join airport on flight.arrival_airport=airport.airport_name where purchase_date>=%s group by airport_city order by c desc)"
    cursor.execute(query,(beginning_date3))
    query="select airport_city from top3dest limit 3"
    cursor.execute(query)
    data=cursor.fetchall()
    top3["last_year"]=[]
    for i in data:
        top3["last_year"].append(i["airport_city"])
    query="drop view if exists top3dest"
    cursor.execute(query)
    session["top3"]=top3
    cursor.close()
    return render_template('airline staff user.html',flight=flights,booking_agent=top5,customer1=customer1,top3=top3,username=session["username"],usertype=session["usertype"])

@app.route('/ASflights',methods=["POST"])
def ASflights():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        error = "Unauthorized!"
        return render_template('home.html', error = error)
    
    source_city=request.form["source city"]
    destination_city=request.form["destination city"]
    date=request.form["date"]

    if source_city=="": ##default
        current_time=datetime.datetime.now()
        last_date=current_time+datetime.timedelta(days=30)
        query="select * from flight natural join airline_staff where username=%s and status='Upcoming' and departure_time<=%s"
        cursor.execute(query,(username,last_date))
        flights=cursor.fetchall()
        return render_template("airline staff view my flights.html",flight=flights)
    else:
        year,month,day=date.split("-")
        query="select * from flight natural join airline_staff where username=%s and departure_airport in (select airport_name from airport where airport_city=%s) and arrival_airport in (select airport_name from airport where airport_city=%s) and extract(year from departure_time)=%s and extract(month from departure_time)=%s and extract(day from departure_time)=%s"
        cursor.execute(query,(username,source_city,destination_city,year,month,day))
        flights=cursor.fetchall()
        return render_template("airline staff view my flights.html",flight=flights)

@app.route('/CRinfo',methods=['GET','POST'])
def CRinfo():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    flight_num=request.form['customer information']
    query="select distinct customer_email from purchases natural join ticket where flight_num=%s"
    cursor.execute(query,(flight_num))
    data=cursor.fetchall()
    cursor.close()
    customers=[]
    for i in data:
        customers.append(i['customer_email'])
    return render_template("CRinfo.html",flight=customers,flight_num=flight_num)
    
@app.route("/createflights",methods=["POST"])
def createflights():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)

    query="select permission_type from permission where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchall()
    indicator=0
    for i in data:
        if i["permission_type"]=="Admin":
            indicator=1
            break
    if indicator==0:
        cursor.close()
        error="You need to get 'Admin' permission for this operation!"
        return render_template("airline staff user.html")

    airline_name=request.form["airline_name"]
    flight_num=request.form["flight_num"]
    departure_airport=request.form["departure_airport"]
    departure_time=request.form["departure_time"]
    arrival_airport=request.form["arrival_airport"]
    arrival_time=request.form["arrival_time"]
    status=request.form["status"]
    price=request.form["price"]
    airplane_id=request.form["airplane_id"]

    query="insert into flight values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(query,(airline_name,flight_num,departure_airport,departure_time,arrival_airport,arrival_time,price,status,airplane_id))
    conn.commit()
    cursor.close()
    return render_template("airline staff user.html",flight=session["flights"],booking_agent=session["top5"],customer1=session["customer1"],top3=session["top3"],username=session["username"],usertype=session["usertype"])

@app.route("/changestatus",methods=["POST"])
def changestatus():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)

    query="select permission_type from permission where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchall()
    indicator=0
    for i in data:
        if i["permission_type"]=="Operator":
            indicator=1
            break
    if indicator==0:
        cursor.close()
        error="You need to get 'Operator' permission for this operation!"
        return render_template("airline staff user.html",flight=session["flights"],booking_agent=session["top5"],customer1=session["customer1"],top3=session["top3"],username=session["username"],usertype=session["usertype"])

    flight_num=request.form['flight']
    status=request.form['status']
    query="update flight set status=%s where flight_num=%s"
    cursor.execute(query,(status,flight_num))
    conn.commit()
    cursor.close()
    return render_template("airline staff user.html",flight=session["flights"],booking_agent=session["top5"],customer1=session["customer1"],top3=session["top3"],username=session["username"],usertype=session["usertype"])
          
@app.route("/addairplane",methods=["POST"])
def addairplane():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)

    query="select permission_type from permission where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchall()
    indicator=0
    for i in data:
        if i["permission_type"]=="Admin":
            indicator=1
            break
    if indicator==0:
        cursor.close()
        error="You need to get 'Admin' permission for this operation!"
        return render_template("airline staff user.html",flight=session["flights"],booking_agent=session["top5"],customer1=session["customer1"],top3=session["top3"],username=session["username"],usertype=session["usertype"])

    airline_name=request.form['airline_name']
    airplane_id=request.form['airplane_id']
    seat_number=request.form["seat number"]
    query="Insert into airplane values(%s,%s,%s)"
    cursor.execute(query,(airline_name,airplane_id,seat_number))
    conn.commit()

    query="select * from airplane where airline_name=%s"
    cursor.execute(query,(session["airline_name"]))
    airplanes=cursor.fetchall()
    cursor.close()
    return render_template("airline staff add airline confirmation.html",airline=airplanes,airline_name=session["airline_name"])

          
@app.route("/addairport",methods=["POST"])
def addairport():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)

    query="select permission_type from permission where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchall()
    indicator=0
    for i in data:
        if i["permission_type"]=="Admin":
            indicator=1
            break
    if indicator==0:
        cursor.close()
        error="You need to get 'Admin' permission for this operation!"
        return render_template("airline staff user.html")

    airport_name=request.form["airport_name"]
    airport_city=request.form["airport_city"]
    query="Insert into airport values(%s,%s)"
    cursor.execute(query,(airport_name,airport_city))
    conn.commit()
    cursor.close()
    return render_template("airline staff user.html",flight=session["flights"],booking_agent=session["top5"],customer1=session["customer1"],top3=session["top3"])

@app.route("/choose_past",methods=["POST"])
def choose_past():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    current_date=datetime.datetime.now()
    past=request.form["past"]
    if past=="past_month":
        beginning_date=current_date-datetime.timedelta(days=30)
    else:
        beginning_date=current_date-datetime.timedelta(days=365)

    query="with temp as (select count(ticket_id) as sales, email from purchases natural join booking_agent where purchase_date>=%s group by email order by sales desc) select * from temp limit 5"
    cursor.execute(query,(beginning_date))
    data=cursor.fetchall()
    cursor.close()
    return render_template("view top booking_agent.html",booking_agent=data)

@app.route("/check_the_flight_of_this_customer",methods=["POST"])
def check_the_flight_of_this_customer():
    username=session['username'] #Auth
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    email=request.form["customer_email"]
    query="select * from flight where airline_name=(select distinct airline_name from airline_staff where username=%s) and flight_num in (select flight_num from ticket natural join purchases where customer_email=%s) "
    cursor.execute(query,(username,email))
    flight=cursor.fetchall()
    cursor.close()
    return render_template("flight information of customer.html",customer=email,flight=flight)

@app.route("/total_amounts_of_ticket",methods=["POST"])
def total_amounts_of_ticket():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)

    day=request.form["date"]
    month=request.form["month"]
    year=request.form["year"]
    def find_x(month,year):
        current_date=datetime.datetime.now().strftime("%Y-%m-%d")
        cyear,cmonth,cday=current_date.split("-")
        cyear=int(cyear)
        cmonth=int(cmonth)
        cday=int(cday)
        temp_month=int(month)
        temp_year=int(year)
        x=[]
        while temp_year!=cyear or temp_month!=cmonth:
            x.append([temp_year,temp_month])
            if (temp_month!=12):
                temp_month+=1
            else:
                temp_year+=1
                temp_month=1
        x.append([temp_year,temp_month])
        return x
    x=find_x(month,year)
    beginning_date=str(year)+"-"+str(month)+"-"+str(day)
    query="drop view if exists temp_AScounter"
    cursor.execute(query)
    query="create view temp_AScounter as (select ticket_id, extract(year from purchase_date) as year, extract(month from purchase_date) as month from purchases where purchase_date>=%s)"
    cursor.execute(query,(beginning_date))
    query="select count(ticket_id) as c,year,month from temp_AScounter group by year,month order by year,month asc"
    cursor.execute(query)
    data=cursor.fetchall()
    y=[]
    y_index=0
    for i in x:
        if int(i[0])!=int(data[y_index]["year"]) or int(i[1])!=int(data[y_index]["month"]):
            y.append(0)
        else:
            y.append(data[y_index]["c"])
            y_index=y_index+1
    query="drop view if exists temp_AScounter"
    cursor.execute(query)
    cursor.close()
    return render_template("airline staff barchart.html",x=x,y=y,total=sum(y))

@app.route("/piechart")
def piechart():
    #Auth
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    
    current_date=datetime.datetime.now()
    beginning_date=beginning_date=current_date-datetime.timedelta(days=365)
    dquery="select sum(price) as s from (ticket left join purchases on ticket.ticket_id=purchases.ticket_id) left join flight on ticket.flight_num=flight.flight_num where booking_agent_id is null and purchase_date>=%s"
    cursor.execute(dquery,(beginning_date))
    data=cursor.fetchall()
    temp1=[]
    for i in data:
        temp1.append(float(i["s"]))
    direct=sum(temp1)
    
    iquery="select sum(price) as s from (ticket left join purchases on ticket.ticket_id=purchases.ticket_id) left join flight on ticket.flight_num=flight.flight_num where booking_agent_id is not null and purchase_date>=%s"
    cursor.execute(iquery,(beginning_date))
    data=cursor.fetchall()
    temp2=[]
    for i in data:
        temp2.append(float(i["s"]))
    indirect=sum(temp2)
    cursor.close()
    return render_template("airline staff piechart.html",data1=direct,data2=indirect)

@app.route('/grant_permission',methods=['POST'])
def ASgrant_permission():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)

    query="select permission_type from permission where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchall()
    indicator=0
    for i in data:
        if i["permission_type"]=="Admin":
            indicator=1
            break
    if indicator==0:
        cursor.close()
        error="You need to get 'Admin' permission for this operation!"
        return render_template("airline staff user.html",flight=session["flights"],booking_agent=session["top5"],customer1=session["customer1"],top3=session["top3"],error=error,username=session["username"],usertype=session["usertype"])
    
    staff=request.form['staff']
    query="select airline_name from airline_staff where username=%s"
    cursor.execute(query,(staff))
    if cursor.fetchone()['airline_name'] not in session["airline_name"]:
        error="You can only give permission to those who are in the same airline with you!"
        return render_template("airline staff user.html",flight=session["flights"],booking_agent=session["top5"],customer1=session["customer1"],top3=session["top3"],error=error,username=session["username"],usertype=session["usertype"])  
    query='Insert into permission values(%s,"Admin")'
    cursor.execute(query, (staff))
    conn.commit()
    cursor.close()
    return render_template("airline staff user.html",flight=session["flights"],booking_agent=session["top5"],customer1=session["customer1"],top3=session["top3"],username=session["username"],usertype=session["usertype"])

@app.route('/add_booking_agent',methods=['POST'])
def ASadd_BA():
    try:
        username=session['username']
    except:
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)
    cursor = conn.cursor()
    query="select * from airline_staff where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchone()
    if (not data):
        cursor.close()
        error = "Unauthorized!"
        session.clear()
        return render_template('home.html', error = error)

    query="select permission_type from permission where username=%s"
    cursor.execute(query,(username))
    data=cursor.fetchall()
    indicator=0
    for i in data:
        if i["permission_type"]=="Admin":
            indicator=1
            break
    if indicator==0:
        cursor.close()
        error="You need to get 'Admin' permission for this operation!"
        return render_template("airline staff user.html")
    
    email=request.form['email']
    cursor=conn.cursor()
    query='Insert into booking_agent_work_for values(%s,%s)'
    cursor.execute(query, (email,session["airline_name"]))
    conn.commit()
    cursor.close()
    return render_template("airline staff user.html",flight=session["flights"],booking_agent=session["top5"],customer1=session["customer1"],top3=session["top3"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/test")
def test():
    customer={}
    customer['total']=2222
    customer['total2']=3333
    customer2="customer!"
    customer3=10
    return render_template("javascript test.html",customer=customer,customer2=customer2,customer3=customer3)

app.secret_key = 'HMSKagami'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
