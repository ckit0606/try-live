import re
import boto3
import os
from pymysql import connections
from flask import Flask, redirect, url_for, request, render_template, session

from datetime import datetime
 
app = Flask(__name__)

bucket = "chunkit-s3-bucket"
region = "us-east-1"

db_conn = connections.Connection(
    host='database-2.cjdu7tfbjxtq.us-east-1.rds.amazonaws.com',
    port=3306,
    user='aws_user',
    password='Bait3273',
    db='chunkit'

)


@app.route("/")
def profile():
    cursor = db_conn.cursor()
    cursor.execute('SELECT * FROM student WHERE StudentID = 1')
    data = cursor.fetchone()

    return render_template("profile.html",data=data)

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    resume_url = ''
    report_url = ''

    if request.method == 'POST':
        studentName = request.form.get("studentName")
        gender = request.form.get("gender")
        programme = request.form.get("programme")
        state = request.form.get("state_select_programme")
        contact = request.form.get("contact")
        studyYear = request.form.get("studyYear")
        method = request.form.get("method")
        resume = request.files.get("resume")
        report = request.files.get("report")
        status = 'Pending'
        studentID = 1

        if resume:    
            pdf_file_name_in_s3 = "Id-" + str(1) + "_resume_pdf"
            s3 = boto3.resource('s3')
            s3.Bucket(bucket).put_object(Key=pdf_file_name_in_s3, Body=resume)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=bucket)
            s3_location = (bucket_location['LocationConstraint'])
            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location
            resume_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                bucket,
                pdf_file_name_in_s3)
            
        if report:    
            pdf_file_name_in_s3 = "Id-" + str(1) + "_report_pdf"
            s3 = boto3.resource('s3')
            s3.Bucket(bucket).put_object(Key=pdf_file_name_in_s3, Body=resume)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=bucket)
            s3_location = (bucket_location['LocationConstraint'])
            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location
            report_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                bucket,
                pdf_file_name_in_s3)

        cursor = db_conn.cursor()
        update_sql = 'UPDATE student SET StudentName = %s, StudentGender = %s, StudentProgramme = %s, StudentState = %s,StudentPhoneNumber = %s,StudentYear = %s,StudentMethod = %s,StudentResume = %s,StudentReport = %s WHERE StudentID = 1'
        cursor.execute(update_sql, (studentName,gender,programme,state,contact,studyYear,method,resume_url,report_url))
        db_conn.commit()
        cursor.close()

        
        if resume:    
            pdf_file_name_in_s3 = "Id-" + str(1) + "_resume_pdf"
            s3 = boto3.resource('s3')
            s3.Bucket(bucket).put_object(Key=pdf_file_name_in_s3, Body=resume)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=bucket)
            s3_location = (bucket_location['LocationConstraint'])
            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location
            resume_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                bucket,
                pdf_file_name_in_s3)
            
        cursor = db_conn.cursor()
        insert_sql = "INSERT INTO resume (StudentID,ResumeLink,ResumeStatus) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (studentID,resume_url,status))
        db_conn.commit()
        cursor.close()

        return redirect(url_for("profile"))

    return render_template("edit.html")

@app.route("/layout/")
def layout():
    return render_template("layout.html")

@app.route("/jobList/")
def jobList():
    # Fetch student data from the database where StudentApplyStatus is 'Pending'
    cursor = db_conn.cursor()
    select_sql = "SELECT JobID, JobTitle, JobSalary FROM jobs WHERE JobStatus = 'Accepted'"
    cursor.execute(select_sql)
    jobData = cursor.fetchall()
    cursor.close()
    return render_template("jobList.html", jobData=jobData)

@app.route("/jobDetail", methods=['GET', 'POST'])
@app.route("/jobDetail/<jobID>", methods=['GET', 'POST'])
def jobDetail(jobID=None):
    jobID=jobID
    if request.method == 'POST':
    # Retrieve data from the form
        StudentID = 1
        ApplicationStatus = "Pending"

        # Insert data into the application table
        cursor = db_conn.cursor()
        insert_sql = "INSERT INTO application (StudentID,JobID,ApplicationStatus) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, (StudentID, jobID, ApplicationStatus))
        db_conn.commit()
        cursor.close()


    # Fetch student data from the database where StudentApplyStatus is 'Pending'
    cursor = db_conn.cursor()
    select_sql = "SELECT JobID, JobTitle, JobSalary FROM jobs WHERE JobID = "+jobID
    cursor.execute(select_sql)
    jobData = cursor.fetchone()
    cursor.close()
    return render_template("jobDetail.html",jobData=jobData)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


