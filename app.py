#=====importing libraries=======
from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.utils import redirect
import numpy as np
import pickle
import smtplib
import secret

#=====Config of Flask App======
app = Flask(__name__)
app.config['SECRET_KEY'] = secret.secret_key

#====Loading LR model======
model = pickle.load(open('LRmodelcopy.pkl', 'rb'))

#====routes for the app=====

#=====Home Page route
@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

#=====About Page route
@app.route('/about')
def about():
    return render_template('about.html')

#=====Contact Page route
@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        txt_msg = request.form['message']
        subject = 'Loan Prediction'
        message = f"Subject: {subject}\n\nName: {name}\n\nMessage: {txt_msg}"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(secret.email, secret.email_password)
        server.sendmail(email, secret.email, message) #1st param is to by whom it is sent and 2nd param is to whom it is sent.
    return render_template('contact.html')

#=====Login Page route
@app.route('/login', methods=['GET','POST'])
def login():
    if 'email' in session:
        return redirect(url_for('prediction'))
    else:
        user_email = secret.email
        user_pass = secret.secret_key
        user_name = secret.name
        if request.method == "POST":
            email = request.form['email']
            password = request.form['password']
            if email == user_email and password == user_pass:
                session['email'] = user_email
                session['name'] = user_name
                return redirect(url_for('prediction'))
        return render_template('login.html')

#=====Logout Page route
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

#=====Prediction Page route
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if 'email' in session:
        if request.method == "POST":
            gender = request.form['gender']
            marriedstatus = request.form['marriedstatus']
            dependents = request.form['dependents']
            education = request.form['education']
            selfemployed = request.form['selfemployed']
            credithistory = request.form['credithistory']
            propertyarea = request.form['propertyarea']
            applicantincome = float(request.form['applicantincome'])
            coapplicantincome = float(request.form['coapplicantincome'])
            loanamount = float(request.form['loanamount'])
            loanamountterm = float(request.form['loanamountterm'])

            # for gender
            if (gender == 'Male'):
                male = 1
            else:
                male = 0

            # for marriedstatus
            if (marriedstatus == 'Yes'):
                married_yes = 1
            else:
                married_yes = 0

            # for dependents
            if (dependents == '1'):
                dependents_1 = 1
                dependents_2 = 0
                dependents_3 = 0
            elif(dependents == '2'):
                dependents_1 = 0
                dependents_2 = 1
                dependents_3 = 0
            elif(dependents=="3+"):
                dependents_1 = 0
                dependents_2 = 0
                dependents_3 = 1
            else:
                dependents_1 = 0
                dependents_2 = 0
                dependents_3 = 0 

            # for education
            if (education == 'Not Graduate'):
                not_graduate = 1
            else:
                not_graduate = 0

            # for selfemployed
            if (selfemployed == 'Yes'):
                employed_yes = 1
            else:
                employed_yes = 0

            # for credithistory
            if (credithistory == 'Yes'):
                credit_yes = 1
            elif (credithistory == 'No'):
                credit_yes = 0.8
            else:
                credit_yes = 0

            # for property area
            if(propertyarea == "Semiurban"):
                semiurban = 1
                urban = 0
            elif(propertyarea=="Urban"):
                semiurban = 0
                urban = 1
            else:
                semiurban = 0
                urban = 0


            ApplicantIncomeLog = np.log(applicantincome)
            TotalIncomeLog = np.log(applicantincome+coapplicantincome)
            LoanAmountLog = np.log(loanamount)
            Loan_Amount_TermLog = np.log(loanamountterm)

            # predicting the result with model
            prediction = model.predict([[credit_yes, ApplicantIncomeLog, TotalIncomeLog, LoanAmountLog, Loan_Amount_TermLog, male, married_yes, dependents_1, dependents_2, dependents_3, not_graduate, employed_yes, semiurban, urban ]])

            if(prediction == "N"):
                prediction =  "not eligible."
            else:
                prediction = "eligible."

            return render_template("result.html", prediction_text="Your loan status is {}".format(prediction), name=session['name'])

        else:
            return render_template("prediction.html")
    else:
        return redirect(url_for('login'))       

# avoids running code again & again
if __name__ == '__main__':
    app.run(debug=True) 