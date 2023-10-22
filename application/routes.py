from application import app, db
from flask import render_template, request
from .forms import PatientForm
from datetime import datetime
import pandas as pd
@app.route('/')
def patient_form():
    form = PatientForm()
    return render_template('patient_form.html', form=form)

@app.route('/result', methods=['POST','GET'])
def result():
    details = PatientForm(request.form)
    symptoms_to_search = details.symptoms.data
    symptom_keywords = ["Irregular pulse","Shortness of breath", "Chest pain","Nausea"]
    symptoms_to_search = [s for s in symptom_keywords if s in symptoms_to_search]
    medications_to_search = details.medication.data.split(",") 
    family_history_to_match = details.family_history.data
    year_to_filter = details.year.data
    year_start = datetime(year_to_filter, 1, 1)
    print(symptoms_to_search)
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
    top_5_diagnoses = list(db.patient_collection1.aggregate(pipeline))
    print(datetime.now()-start_time)
    result = list(db.patient_collection1.find(query))
    df = pd.DataFrame(result)
    grouped = df.groupby('Diagnosis Name').size().reset_index(name='patient_count')
    top_5_diagnoses = grouped.sort_values(by='patient_count', ascending=False).head(5)
    total_patients_in_top_5 = 0
    total_patients_in_top_5 = top_5_diagnoses['patient_count'].sum()
    top_5_diagnoses['percentage'] = (top_5_diagnoses['patient_count'] / total_patients_in_top_5 * 100).round(2)
    # Convert the top 5 diagnoses to a dictionary
    top_5_diagnoses_dict = top_5_diagnoses.to_dict(orient='records')
    end_time = datetime.now()
    print("Time taken to execute query:", end_time - start_time)
    return render_template('result.html',df = df, result=top_5_diagnoses_dict,time = end_time - start_time,count = total_patients_in_top_5)