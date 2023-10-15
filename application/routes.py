from application import app, db
from flask import render_template, request
from .forms import PatientForm
from datetime import datetime

@app.route('/')
def patient_form():
    form = PatientForm()
    return render_template('patient_form.html', form=form)

@app.route('/result', methods=['POST','GET'])
def result():
    details = PatientForm(request.form)
    symptoms_to_search = details.symptoms.data.split(",")
    medications_to_search = details.medication.data.split(",") 
    family_history_to_match = details.family_history.data
    year_to_filter = details.year.data
    year_start = datetime(year_to_filter, 1, 1)

    query = {
    "Final Diagnosis Date": {"$gte": year_start},
    "$or": [
        {"Symptoms": {"$in": symptoms_to_search}},
        {"Medications": {"$in": medications_to_search}},
        {"Family History": family_history_to_match}
        ]
    }

    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$Diagnosis Name", "patient_count": {"$sum": 1}}},
        {"$sort": {"patient_count": -1}},
        {"$limit": 5}
    ]

    start_time = datetime.now()
    result = list(db.patient_collection1.aggregate(pipeline))
    end_time = datetime.now()

    total_patients_in_top_5 = 0
    for entry in result:
        total_patients_in_top_5 += entry["patient_count"]

    print("Time taken to execute query:", end_time - start_time)
    print("\n")
    print("Disease Name | Number of Matched Patients | Percentage in Top 5 Patients (%)")
    for entry in result:
        disease_name = entry["_id"]
        patient_count = entry["patient_count"]
        percentage_in_top_5 = patient_count / total_patients_in_top_5 * 100
        print(f"{disease_name} | {patient_count} | {percentage_in_top_5:.2f}%")
        
    return render_template('result.html',result=result,time = end_time - start_time,count = total_patients_in_top_5)