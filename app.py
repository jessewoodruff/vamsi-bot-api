# Using flask to make an api
# import necessary libraries and functions
from flask import Flask, jsonify, request,send_file,send_from_directory
from flask_mail import Mail, Message
from fpdf import FPDF, HTMLMixin
import os
import smtplib
import pandas as pd
import re
import json

# creating a Flask app
app = Flask(__name__)
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'jnjtprmtest@gmail.com',
    "MAIL_PASSWORD": 'Test@2021'
}

#congiguring app settings
app.config.update(mail_settings)
app.config["CLIENT_PDF"] = "C:\\Users\\SA-JNJ-ISRM-GENIE\\Desktop\\j"
#app.config["SERVER_NAME"] = "10.75.179.199:5000" # added by Na Li
mail = Mail(app)

#creating global variables
vendor_name_col = "vendor_company_name_clean"
asset_name_col = "name"

#route to get the similar vendorname using user input string
@app.route('/Get_Vendor_Name', methods = ['GET', 'POST'])
def getVendor():
    df1 = pd.read_csv("rm_organization_1012938_bpraforedl.csv",encoding = 'unicode_escape', engine ='python') # load the dataset
    user_String_Vendor = request.args.get('Vendor_Name') # get user string input
    print(df1[vendor_name_col])
    result_Vendor = df1[df1[vendor_name_col].str.lower().str.contains(user_String_Vendor.lower(),na=False)] # match the string input with vendor names in dataset
    if (result_Vendor.empty):
        response_Vendor = {'status': 'no record found'} # response
        json_Vendor = json.dumps(response_Vendor) # json formatted
        return json_Vendor # output VendorNames
    else:       
        result_Vendor.drop_duplicates(subset = [vendor_name_col], keep = 'first', inplace = True) # vendor name has duplicates
        num_result_Vendor = len(result_Vendor.index)
        print("Bot: we found %s records for you" %num_result_Vendor)   
        response_Vendor = {'Vendor_Name': [i for i in result_Vendor[vendor_name_col]],'status':'records found'} # response
        json_Vendor =json.dumps(response_Vendor) # json formatted
        return json_Vendor # output VendorNames

#route to get the vendor details to display the user
@app.route('/Get_Vendor_Details', methods = ['GET', 'POST'])
def VendorDetails():
    df2 = pd.read_csv("rm_organization_1012938_bpraforedl.csv",encoding = 'unicode_escape', engine ='python') #load the dataset
    df2['status']= 'records found'
    actual_Asset = request.args.get('Actual_Vendor').lower() #get uset asset name
    response_Vendor_Details = df2[df2[asset_name_col].str.lower()==actual_Asset] #match asset name with the dataset asset name
    if(response_Vendor_Details.empty):
       response_Vendor_Details_Final = {'status': 'no record found'} # response
       json_Vendor_Details = json.dumps(response_Vendor_Details_Final) # json formatted
       return json_Vendor_Details # output VendorNames
    else:
       result_Vendor_Details = response_Vendor_Details.to_json(orient="records") # orient the records
       parsed_Vendor_Details = json.loads(result_Vendor_Details) #json formatted
       json_Vendor_Details = json.dumps(parsed_Vendor_Details, indent=4)
       #result_Details = json_Vendor_Details + json_Vendor
       return json_Vendor_Details # output

#route to get the vendor asset details
@app.route('/Get_Vendor_Asset', methods = ['GET', 'POST'])
def VendorAsset():
    df3 = pd.read_csv("rm_organization_1012938_bpraforedl.csv",encoding = 'unicode_escape', engine ='python') # load the dataset
    actual_Vendor = request.args.get('Actual_Vendor') # get the vendor name
    result_Asset = df3[df3[vendor_name_col] == actual_Vendor] # match the vendor name with the dataset vendor
    num_result_Asset = len(result_Asset.index)
    print("Bot: we found %s records for you" %num_result_Asset)  
    response_Asset = {'Asset_Name': [i for i in result_Asset[asset_name_col]],'status':'records found'} # retreive asset names
    json_Asset = json.dumps(response_Asset) # json formatted
    return json_Asset # output

#route to send email using smtp library and gmail login credentials
# can utilize it if needed in future.
@app.route('/Send_Email', methods = ['GET', 'POST'])
def sendMail():
    #df = pd.read_csv(data_path,encoding = 'unicode_escape', engine ='python')
    #input_string = request.args.get('Email_Body')
    subject_str = request.args.get('subject')
    recipients_str = ['pvadapal@its.jnj.com','nli51@its.jnj.com','sdrew3@its.jnj.com','sson5@its.jnj.com']
    body_str = request.args.get('body')
    msg = Message(subject=subject_str,
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=recipients_str, # use your email for testing
                      body=body_str)
    mail.send(msg)
    return 'sent'

#route to create vendor details in pdf and get the pdf url to display the user
@app.route('/Get_pdf', methods = ['GET', 'POST'])
def testJSONtoPDF():
    class MyFPDF(FPDF, HTMLMixin):
        pass
    input_string = request.args.get('body')
    username = request.args.get('name')
    pdf = MyFPDF()
    pdf.add_page()
    pdf.write_html(input_string)
    path_Store_Pdf = 'C:\\Users\\SA-JNJ-ISRM-GENIE\\Desktop\\j\\'+username+'.pdf'
    print(path)
    pdf.output(path_Store_Pdf, 'F')
    path_inside = 'http://10.75.179.199:9000/Desktop/j/'+username+'.pdf'
    response_Pdf = {'File_Url': path_inside}
    json_Pdf = json.dumps(response_Pdf)
    return json_Pdf

#function for waitress by Gaurav
def create_app():
    return app

# driver function
if __name__ == '__main__':

    app.run(host="0.0.0.0",debug = True,port=8000)
