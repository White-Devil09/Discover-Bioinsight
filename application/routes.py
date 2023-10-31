from application import app, db
from flask import render_template, request, redirect, url_for
from .forms import PatientForm
from datetime import datetime
import pandas as pd
from collections import defaultdict
import json
from collections import Counter
import re

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/platform')
def platform():
    return render_template('platform.html')

@app.route('/contact')
def contact_us():
    return "Hello contact"

@app.route('/coming_soon')
def coming_soon():
    return " This page is under construction"

@app.route('/patient_form', methods=['POST','GET'])
def patient_form():
    form = PatientForm()
    return render_template('patient_form.html', form=form)

@app.route('/result', methods=['POST','GET'])
def result():
    details = PatientForm(request.form)
    symptoms_freetext = details.symptoms.data.lower()
    symptom_keywords = ['dizziness', 'restlessness', 'swelling in the ankles', 'severe headache', 'pain in the arm', 'pain in the shoulder', 
                        'shortness of breath', 'feeling of indigestion', 'swelling in ankles', 'cough especially when lying down', 
                        'palpitations', 'fatigue', 'wheezing', 'feeling of heartburn', 'feeling of fullness', 'loss of consciousness', 
                        'cyanosis (bluish or grayish skin color)', 'sweating', 'nausea', 'cold sweats', 'blurry vision', 'chest pain', 'fainting', 
                        'cold sweat', 'pain in the neck', 'pain in the jaw', 'irregular pulse', 'difficulty concentrating', 'headache', 'weakness']
    symptoms_to_search = [s for s in symptom_keywords if s in symptoms_freetext]
    
    medication_keywords = ['aspirin', 'pioglitazone', 'simvastatin', 'linagliptin', 'isosorbide mononitrate', 'none', 'diltiazem', 'insulin', 'glyburide', 'glipizide', 'atorvastatin',
                            'empagliflozin', 'ezetimibe', 'amlodipine', 'sitagliptin', 'hydrochlorothiazide', 'lovastatin', 'glimepiride', 'spironolactone', 'canagliflozin', 'dabigatran',
                              'pravastatin', 'carvedilol', 'cilostazol', 'clopidogrel', 'metformin', 'gemfibrozil', 'rivaroxaban',
                            'exenatide', 'enalapril', 'warfarin', 'metoprolol', 'atenolol', 'losartan', 'lisinopril', 'furosemide', 'prasugrel', 'apixaban', 'rosuvastatin', 'valsartan']
    medications_free_text = details.medication.data.lower()
    medications_to_search =  [s for s in medication_keywords if s in medications_free_text]
    family_history_to_match = details.family_history.data.lower()
    family_history_list = []
    family_history_list.append(family_history_to_match)
    past_medical_history = details.pastmedical_history.data.lower()
    past_medical_history_list = []
    past_medical_history_list.append(past_medical_history)
    bmi_index = details.Weight.data / (details.Height.data/100)**2
    family_history_to_match = details.family_history.data
    year_to_filter = details.year.data
    to_year_to_filter = details.to_year.data
    print(year_to_filter)
    print(symptoms_to_search)
    query = {
        "$and": [
            {
                "Final Diagnosis Date": {
                    "$gte": year_to_filter,
                    "$lte": to_year_to_filter
                }
            },
            {
                "$or": [
                    {
                        "Symptoms": {
                            "$elemMatch": {
                                "$in": symptoms_to_search
                            }
                        }
                    },
                    {
                        "Medications": {
                            "$elemMatch": {
                                "$in": medications_to_search
                            }
                        }
                    },
                    {
                        "Family History": {
                            "$regex": family_history_to_match,
                            "$options": "i"
                        }
                    },
                    {
                        "Past Medical History": {
                            "$in": past_medical_history_list
                        }
                    }
                ]
            }
        ]
    }

    pipeline = [
        {
            "$match": query
        },
        {
            "$group": {
                "_id": "$Diagnosis Name",
                "count": { "$sum": 1 },
                "data": { "$push": "$$ROOT" }
            }
        },
        {
            "$sort": {"count": -1}
        },
        {
            "$limit": 5
        },
        {
            "$unwind" : "$data"
        },
        {
            "$replaceRoot": { "newRoot": "$data" }
        }
    ]
    start_time = datetime.now()
    cursor = list(db.patient_collection1.aggregate(pipeline))

    df = pd.DataFrame(cursor)
    if df.empty:
        return redirect(url_for('patient_form'))
    grouped = df.groupby("Diagnosis Name").size().reset_index(name="patient_count")
    top_5_diagnoses = grouped.sort_values(by="patient_count", ascending=False).head(5)
    top_diagnoses_names = top_5_diagnoses['Diagnosis Name'].tolist()


    total_patients_in_top_5 = 0
    total_patients_in_top_5 = top_5_diagnoses["patient_count"].sum()
    top_5_diagnoses['percentage'] = (top_5_diagnoses["patient_count"] / total_patients_in_top_5 * 100).round(2)



    # smoker_calculation
    daily_counts = [sum((df['Smoker'] == 'Daily') & (df['Diagnosis Name'] == diag)) for diag in top_5_diagnoses['Diagnosis Name']]
    never_counts = [sum((df['Smoker'] == 'Never') & (df['Diagnosis Name'] == diag)) for diag in top_5_diagnoses['Diagnosis Name']]
    occasionally_counts = [sum((df['Smoker'] == 'Occasionally') & (df['Diagnosis Name'] == diag)) for diag in top_5_diagnoses['Diagnosis Name']]
    quit_smoking_counts = [sum((df['Smoker'] == 'Quit smoking') & (df['Diagnosis Name'] == diag)) for diag in top_5_diagnoses['Diagnosis Name']]

    top_5_diagnoses['daily_count'] = daily_counts
    top_5_diagnoses['never_count'] = never_counts
    top_5_diagnoses['occasionally_count'] = occasionally_counts
    top_5_diagnoses['quit_smoking_count'] = quit_smoking_counts


    symptom_data_by_diagnosis = {}
    medication_data_by_diagnosis = {}
    family_history_by_diagnosis = {}
    region_symptom_data = {}
    region_counts = {}
    sex_chart_data = {}
    past_medical_history= {}
    # symptoms and medications calculations
    for disease_name in top_5_diagnoses['Diagnosis Name']:
        patients_for_disease = df[df["Diagnosis Name"] == disease_name]
        all_symptoms = [symptom for patient in patients_for_disease["Symptoms"] for symptom in patient]  # Iterate through the "Symptoms" column of each patient's DataFrame
        top_symptoms = pd.Series(all_symptoms).value_counts().head(5)

        # Calculate percentages
        total_patients = len(patients_for_disease)
        symptom_counts = pd.Series(all_symptoms).value_counts()
        # Store symptom data for this diagnosis
        symptom_data_by_diagnosis[disease_name] = {
            "top_symptoms": top_symptoms.index.tolist(),
            "percentage": symptom_counts.tolist()
        }

        all_family_histories = patients_for_disease['Family History']
        family_history_counts = all_family_histories.value_counts().head(7).to_dict()
        family_history_by_diagnosis[disease_name] = {
            'labels': list(family_history_counts.keys()),
            'data': list(family_history_counts.values()),
        }

        all_past_medical_history = patients_for_disease['Past Medical History']
        past_medical_history_counts = all_past_medical_history.value_counts().head(5).to_dict()
        past_medical_history[disease_name] = {
            'labels': list(past_medical_history_counts.keys()),
            'data': list(past_medical_history_counts.values()),
        }


        medications_counts = patients_for_disease['Medications'].explode().value_counts().head(7).to_dict()
        # Prepare the data for the pie chart
        medications_labels = list(medications_counts.keys())
        medications_data = list(medications_counts.values())

        # Store the data in the medications_chart_data dictionary
        medication_data_by_diagnosis[disease_name] = {
            'labels': medications_labels,
            'data': medications_data,
        }
        patients_for_disease = patients_for_disease.explode('Symptoms')
        top_symptoms = patients_for_disease['Symptoms'].value_counts().head(5).index.tolist()
        grouped = patients_for_disease.groupby(['Region Of Origin', 'Symptoms']).size().unstack(fill_value = 0)
        grouped = grouped[top_symptoms]
        region_symptom_data[disease_name] = {
            'top_symptoms': top_symptoms,
            'region_data': grouped.to_dict(orient='split'),
        }


    for diagnosis_name in top_diagnoses_names:
        diagnosis_df = df[df['Diagnosis Name'] == diagnosis_name]
        region_counts[diagnosis_name] = diagnosis_df['Region Of Origin'].value_counts().to_dict()
        sex_counts = diagnosis_df['Gender'].value_counts().to_dict()
        sex_labels = list(sex_counts.keys())
        sex_data = list(sex_counts.values())
        sex_chart_data[diagnosis_name] = {
            'labels':sex_labels,
            'data':sex_data,
        }

    sex_chart_data_json = json.dumps(sex_chart_data)


    # age range distribution heatmap:
    age_ranges = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# Initialize a dictionary to store symptom frequencies by age range for each diagnosis name
    symptom_data_by_diagnosis_age_range = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

# Iterate through rows in the DataFrame
    for index, row in df.iterrows():
        diagnosis_name = row['Diagnosis Name']
        age = row['Age']
        symptoms = row['Symptoms']

        # Categorize age into the appropriate age range
        for i in range(len(age_ranges) - 1):
            if age_ranges[i] <= age < age_ranges[i + 1]:
                age_range = f"{age_ranges[i]}-{age_ranges[i + 1]}"
                break
        else:
            # If the age is above the last range, categorize it as "90-100+"
            age_range = f"{age_ranges[-1]}+"

        # Increment the count of symptoms for the current diagnosis name, age range, and symptom
        for symptom in symptoms:
            if symptom in symptoms_to_search:
                symptom_data_by_diagnosis_age_range[diagnosis_name][age_range][symptom] += 1



    bmi_ranges = [0, 18.5, 24.9, 29.9, 34.9, 39.9, 100]
    bmi_labels = ['Underweight [0-18.5]', 'Normal Weight [18.5-24.9]', 'Overweight [24.9-29.9]', 'Obesity I [29.9-34.9]', 'Obesity II [34.9-39.9]', 'Obesity III [>39.9]']

    # Use pandas' cut function to categorize BMI into ranges
    df['BMI Category'] = pd.cut(df['BMI Index'], bins=bmi_ranges, labels=bmi_labels)
    bmi_histogram_dict = {}
    for diagnosis_name, group in df.groupby('Diagnosis Name'):
        # Calculate the BMI index histogram for the current diagnosis
        bmi_histogram = group['BMI Category'].value_counts().sort_index().to_dict()
        bmi_histogram_dict[diagnosis_name] = bmi_histogram
    top_5_diagnoses_dict = top_5_diagnoses.to_dict(orient='records')

    
    medications_chart_data_json = json.dumps(medication_data_by_diagnosis)
    family_history_by_diagnosis_json = json.dumps(family_history_by_diagnosis)
    past_medical_history = json.dumps(past_medical_history)
    end_time = datetime.now()
    print("Time taken to execute query:", end_time - start_time)


    return render_template('result.html', bmi_histogram_dict=bmi_histogram_dict , result=top_5_diagnoses_dict,time = end_time - start_time,count = total_patients_in_top_5, symptom_data_by_diagnosis=symptom_data_by_diagnosis,
                            region_counts=region_counts,symptom_data_by_diagnosis_age_range=symptom_data_by_diagnosis_age_range,
                            gender_chart = sex_chart_data_json, medications_chart_data_ = medications_chart_data_json,past_medical_history = past_medical_history,
                            family_history_by_diagnosis_json=family_history_by_diagnosis_json, region_symptom_data = region_symptom_data, bmi_index = bmi_index)
