# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request,redirect,url_for,jsonify
from flask_login import login_required
from jinja2 import TemplateNotFound
import json
from datetime import datetime, timedelta
from datetime import datetime
import json
from flask import jsonify
import os

# Get the current working directory
current_directory = os.getcwd()

print("Current Directory:", current_directory)
global jsonath2
new=os.path.join(current_directory,'apps')
jsonath1=os.path.join(new,'customer_detail.json')
jsonath2=os.path.join(new,'customer_point_transaction.json')




with open(jsonath1, 'r') as file:
    data = json.load(file)

with open(jsonath2, 'r') as file1:
    data1=json.load(file1)

existing_data=data1

currentdate = datetime.now()
three_months_ago = currentdate - timedelta(days=90)
one = currentdate - timedelta(days=1)


@blueprint.route('/index')
@login_required
def index():
    
    cuslist = [doc for doc in data]

    #----------------------------------------Total Sales
    total_sales = sum(int(entry["bill_amount"]) for entry in data1)

    #----------------------------------------Last 3 month Sales
    filtered_data = [entry for entry in data1 if datetime.strptime(entry["created_on"], "%Y-%m-%d %H:%M:%S") >= three_months_ago]
    last_3_month_sales = sum(int(entry["bill_amount"]) for entry in filtered_data)

    #----------------------------------------Today Sales

    filtered_data1 = [entry for entry in data1 if datetime.strptime(entry["created_on"], "%Y-%m-%d %H:%M:%S") >= one]
    last_7_sales = sum(int(entry["bill_amount"]) for entry in filtered_data1)

    #-----------------------------------------Recent customer
    customer_data = sorted(data, key=lambda x: x['created_on'], reverse=True)

    latest_5_customers = customer_data[:5]

    #-------------total customer
    totalcus=len(cuslist)

    #-------------total points

    total_points = sum(entry["points"] for entry in data)


    #-------------------Last Week sales

    date_format = "%Y-%m-%d %H:%M:%S"

    current_datetime = datetime.now()

    start_of_last_week = current_datetime - timedelta(days=current_datetime.weekday() + 7)

    filtered_data2 = [entry for entry in data1 if datetime.strptime(entry["created_on"], "%Y-%m-%d %H:%M:%S") >= start_of_last_week]

    

    date_format = "%Y-%m-%d %H:%M:%S"

    current_datetime = datetime.now()

    # Calculate the start date of the last week

    start_of_last_week = current_datetime - timedelta(days=current_datetime.weekday() + 7)

    # Filter sales records for the last week
    last_week_sales1 = [sale for sale in data1 if datetime.strptime(sale['created_on'], date_format) >= start_of_last_week]

    last_week_sales2 = [sale for sale in data if datetime.strptime(sale['created_on'], date_format) >= start_of_last_week]

    Today_data = [sale for sale in data if datetime.strptime(sale['created_on'], date_format).date() == current_datetime.date()]

    # last_week_sales 

    last_week_sales=sum(int(sale['bill_amount']) for sale in last_week_sales1)
    
    


    #---------------Last week total visit
    last_week_visits = len(last_week_sales1)

    

    return render_template('home/index.html', segment='index',inventory_data=cuslist,total_sales=total_sales,last_3_month_sales=last_3_month_sales,
    last_7_sales=last_7_sales,latest_5_customers=latest_5_customers,totalcus=totalcus,total_points=total_points,last_week_sales=last_week_sales,last_week_visits=last_week_visits,
    last_week_sales2=last_week_sales2,Today_data=Today_data)

    


@blueprint.route('/<template>')
@login_required
def route_template(template):

    
    # for document in documents:
    #     print(document)

    data = [doc for doc in data1]

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment,inventory_data=data)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


@blueprint.route("/addsale", methods=["POST"])
def additem():
    mbl = request.form.get("mobile")
    vrch = request.form.get("Voucher")
    AMOUNT = request.form.get("Amount")
    Notes = request.form.get("Notes")
    
    import json

    # Read existing JSON data from the file
    file_path = jsonath2

    with open(file_path, 'r') as file:
        existing_data = json.load(file)

    POINT=int(AMOUNT)//100
    # Append new data to the existing array
    new_data = {
        "bill_amount": AMOUNT,
        "created_on": "2024-01-01 14:45:00",
        "current_points": 1,
        "id": 4,
        "invoice_no": vrch,
        "mobile_number": mbl,
        "point_add": 15,
        "point_type": 1,
        "remark": Notes,
        "sale_by": 3
    }

    existing_data.append(new_data)

    # Write the updated data back to the file
    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=2)

    print("Data appended successfully.")


    return redirect(url_for('home_blueprint.index'))

  
@blueprint.route('/redeempoint', methods=["POST"])
def redeempoint():
    mobile=request.form.get('mobile')
    point=request.form.get('point')

    print(mobile)
    print(point)

    import requests

    totalpoint=0
    uid=0
    user_result=''
    def reduce_points(json_file, mobile_number, points_to_deduct):
        with open(json_file, 'r') as file:
            user_data = json.load(file)

        user_found = False

        for user in user_data:
            if user["mobile"] == mobile_number:
                current_points = user["points"]
                if current_points >= points_to_deduct:
                    user["points"] -= points_to_deduct
                    
                    user_found = True

                
                else:
                    print(f"Insufficient points for user with mobile number {mobile_number}")

        if not user_found:
            print(f"No user found with mobile number {mobile_number}")

        if user_found is True:
            with open(file_path, 'r') as file:
                existing_data = json.load(file)

            # Append new data to the existing array
            new_data = {
                "bill_amount": 0,
                "created_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "current_points": user["points"],
                "id": user['id'],
                "invoice_no": "",
                "mobile_number": mobile_number,
                "point_add": int(point),
                "point_type": 2,
                "remark": "",
                "sale_by": 1
            }

            existing_data.append(new_data)

            # Write the updated data back to the file
            with open(file_path, 'w') as file:
                json.dump(existing_data, file, indent=2)

            print("Data appended successfully.")
            print({'message': 'Data added successfully', 'inventory': new_data})
    

        with open(json_file, 'w') as file:
            json.dump(user_data, file, indent=2)

    def search_by_mobile(json_file, mobile_number):
        with open(json_file, 'r') as file:
            user_data = json.load(file)

        for user in user_data:
            if user["mobile"] == mobile_number:
                return user
        return None

    # Example usage:
    json_file_path = jsonath1
    mobile_to_search = mobile

    result = search_by_mobile(json_file_path, mobile_to_search)

    print(result)

    print(user_result)

    
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/redeemcoupan', methods=["POST"])
def redeemcoupan():
    mobile=request.form.get('mobile')
    coupan=request.form.get('coupan')

    print(mobile)
    print(coupan)
    
    return redirect(url_for('home_blueprint.index'))


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
