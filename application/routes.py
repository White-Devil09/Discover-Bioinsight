from application import app
from flask import render_template, request
from .forms import PatientForm
from datetime import datetime
import pandas as pd
from collections import defaultdict
import json
import sqlite3
import ast

def convert_to_list(s):
    if pd.isna(s) or s == '[]' or s == '':
        return []  # Return an empty list
    else:
        try:
            return ast.literal_eval(s)  # Convert the string to a list
        except (SyntaxError, ValueError):
            return [s]

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
def patient_form(show_alert=False):
    form = PatientForm()
    return render_template('patient_form.html',show_alert=show_alert, form=form, show_content=True)

@app.route('/result', methods=['POST','GET'])
def result():
    details = PatientForm(request.form)
    symptoms_to_search = []
    symptoms_freetext = details.symptoms.data.lower()
    symptom_keywords = ['dizziness', 'restlessness', 'swelling in the ankles', 'severe headache', 'pain in the arm', 'pain in the shoulder', 
                        'shortness of breath', 'feeling of indigestion', 'swelling in ankles', 'cough especially when lying down', 
                        'palpitations', 'fatigue', 'wheezing', 'feeling of heartburn', 'feeling of fullness', 'loss of consciousness', 
                        'cyanosis (bluish or grayish skin color)', 'sweating', 'nausea', 'cold sweats', 'blurry vision', 'chest pain', 'fainting', 
                        'cold sweat', 'pain in the neck', 'pain in the jaw', 'irregular pulse', 'difficulty concentrating', 'headache', 'weakness']
    symptoms_to_search = [s for s in symptom_keywords if s in symptoms_freetext]
    medications_to_search = []
    medication_keywords = ['aspirin', 'pioglitazone', 'simvastatin', 'linagliptin', 'isosorbide mononitrate', 'none', 'diltiazem', 'insulin', 'glyburide', 'glipizide', 'atorvastatin',
                            'empagliflozin', 'ezetimibe', 'amlodipine', 'sitagliptin', 'hydrochlorothiazide', 'lovastatin', 'glimepiride', 'spironolactone', 'canagliflozin', 'dabigatran',
                              'pravastatin', 'carvedilol', 'cilostazol', 'clopidogrel', 'metformin', 'gemfibrozil', 'rivaroxaban',
                            'exenatide', 'enalapril', 'warfarin', 'metoprolol', 'atenolol', 'losartan', 'lisinopril', 'furosemide', 'prasugrel', 'apixaban', 'rosuvastatin', 'valsartan']
    medications_free_text = details.medication.data.lower()
    medications_to_search =  [s for s in medication_keywords if s in medications_free_text]


    family_history_to_match = details.family_history.data.lower()
    family_history_list = []
    family_history_keywords = ['hyperlipidemia', 'hypertension', 'inflammatory bowel disease ibd', 'hemorrhoids', 'osteoarthritis', 'gout', 'coronary artery disease','drug abuse', 'peptic ulcer disease',
                               'depression', 'congestive heart failure', 'irritable bowel syndrome ibs', 'high blood pressure during pregnancy preeclampsia', 'psoriasis','cataracts', 'dementia', "parkinson's disease",
                                'family history of heart disease', 'prostate enlargement bph','rheumatoid arthritis', 'thyroid disorders', 'smoking', 'glaucoma','osteoporosis', 'erectile dysfunction', 'chronic liver disease'
                                'cancer various types', 'gallstones', 'alcoholism', 'multiple sclerosis', 'polycystic ovary syndrome pcos', 'angina pectoris', 'stroke', 'asthma','kidney stones', 'anxiety', 'chronic kidney disease',
                                'hearing loss', 'obesity', 'peripheral artery disease', 'myocardial infarction heart attack', 'diverticulitis', 'sleep apnea', 'obstructive pulmonary disease copd',
                                'gestational diabetes', 'chronic gastritis', 'atrial fibrillation', 'type 2 diabetes','migraine headaches']
    family_history_list = [s for s in family_history_keywords if s in family_history_to_match]

    past_medical_history = details.pastmedical_history.data.lower()
    past_medical_history_list = []
    past_medical_history_keywords = ['obesity', 'cancer various types' ,'gallstones' 'psoriasis' ,'cataracts' ,'anxiety' ,'erectile dysfunction', 'gestational diabetes', 'high blood pressure during pregnancy preeclampsia',
                                        'smoking','rheumatoid arthritis', 'depression', 'chronic liver disease', 'asthma', 'dementia', 'family history of heart disease', 'type 2 diabetes',
                                        'peptic ulcer disease', 'myocardial infarction heart attack', 'obstructive pulmonary disease copd', 'multiple sclerosis''polycystic ovary syndrome pcos' ,
                                        'glaucoma', 'congestive heart failure','hypertension', 'hearing loss', 'inflammatory bowel disease ibd', 'irritable bowel syndrome ibs', 'sleep apnea', "parkinson's disease"
                                        'thyroid disorders', 'prostate enlargement bph', 'diverticulitis', 'osteoporosis', 'coronary artery disease', 'alcoholism', 'osteoarthritis',
                                        'hyperlipidemia', 'kidney stones', 'chronic kidney disease', 'angina pectoris', 'hemorrhoids', 'migraine headaches', 'peripheral artery disease', 'gout',
                                        'stroke', 'drug abuse', 'chronic gastritis', 'atrial fibrillation']
    past_medical_history_list = [s for s in past_medical_history_keywords if s in past_medical_history]
    weight = details.Weight.data
    height = details.Height.data * float(1)
    if details.weight_units.data == 'lbs':
        weight = weight / 2.205
    if details.Height_units.data == 'feets':
        height = height * 30.48

    bmi_index = weight / ((height+1)/100)**2
    family_history_to_match = details.family_history.data
    year_to_filter = details.year.data
    to_year_to_filter = details.to_year.data

    if not symptoms_to_search:
        symptoms_to_search = ['default']
    if not medications_to_search:
        medications_to_search = ['default']
    if not family_history_list:
        family_history_list = ['default']
    if not past_medical_history_list:
        past_medical_history_list = ['default']


    symptom_params = ['%' + symptom + '%' for symptom in symptoms_to_search]
    medication_params = ['%' + medication + '%' for medication in medications_to_search]
    family_history_params = ['%' + family_history + '%' for family_history in family_history_list]
    past_medical_history_params = ['%' + past_medical_history + '%' for past_medical_history in past_medical_history_list]
    conn = sqlite3.connect('database_exp.db')
    cursor = conn.cursor()
    sql_query = f'''
    SELECT * FROM patient_data
    WHERE (
        {(' OR '.join(["Symptoms LIKE ?" for _ in symptoms_to_search]) if symptoms_to_search else '1=1')}
        OR {(' OR '.join(["Medications LIKE ?" for _ in medications_to_search]) if medications_to_search else '1=1')}
        OR {(' OR '.join(["PastMedicalHistory LIKE ?" for _ in past_medical_history_list]) if past_medical_history_list else '1=1')}
        OR {(' OR '.join(["FamilyHistory LIKE ?" for _ in family_history_list]) if family_history_list else '1=1')}
    )
    AND "FinalDiagnosisDate" BETWEEN ? AND ?
    '''
    params = symptom_params + medication_params + family_history_params+past_medical_history_params+[year_to_filter, to_year_to_filter]
    start_time = datetime.now()
    cursor.execute(sql_query, params)
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])

    if df.empty:
        return patient_form(show_alert=True)
    
    column_name_mapping = {
        'RegionOfOrigin': 'Region Of Origin',
        'PastMedicalHistory': 'Past Medical History',
        'FamilyHistory': 'Family History',
        'FinalDiagnosisDate' : 'Final Diagnosis Date',
        'DiagnosisName':'Diagnosis Name',
        'BMIIndex':'BMI Index',
    }
    df = df.rename(columns=column_name_mapping)

    grouped = df.groupby("Diagnosis Name").size().reset_index(name="patient_count")
    top_5_diagnoses = grouped.sort_values(by="patient_count", ascending=False).head(5)
    top_diagnoses_names = top_5_diagnoses['Diagnosis Name'].tolist()

    df = df[df['Diagnosis Name'].isin(top_diagnoses_names)]

    total_patients_in_top_5 = 0
    total_patients_in_top_5 = top_5_diagnoses["patient_count"].sum()
    top_5_diagnoses['percentage'] = (top_5_diagnoses["patient_count"] / total_patients_in_top_5 * 100).round(2)



    # smoker_calculation
    df['Symptoms'] = df['Symptoms'].apply(lambda x: ast.literal_eval(x))
    df['Medications'] = df['Medications'].apply(convert_to_list)

    symptom_data_by_diagnosis = {}
    medication_data_by_diagnosis = {}
    family_history_by_diagnosis = {}
    region_symptom_data = {}
    region_counts = {}
    sex_chart_data = {}
    past_medical_history= {}
    smoker_counts_by_diagnosis = {}
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
        all_smoking = patients_for_disease['Smoker']
        smoker_counts = all_smoking.value_counts().to_dict()
        smoker_counts_by_diagnosis[disease_name] = {
            'labels': list(smoker_counts.keys()),
            'data': list(smoker_counts.values()),
        }
        all_past_medical_history = patients_for_disease['Past Medical History']
        past_medical_history_counts = all_past_medical_history.value_counts().head(5).to_dict()
        past_medical_history[disease_name] = {
            'labels': list(past_medical_history_counts.keys()),
            'data': list(past_medical_history_counts.values()),
        }
        medications_counts = patients_for_disease['Medications'].explode().value_counts().head(7).to_dict()
        medications_labels = list(medications_counts.keys())
        medications_data = list(medications_counts.values())
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
        all_regions = patients_for_disease['Region Of Origin']
        region_count = all_regions.value_counts().to_dict()
        region_counts[disease_name] = {
            'labels' : list(region_count.keys()),
            'data' : list(region_count.values()),
        }




    for diagnosis_name in top_diagnoses_names:
        diagnosis_df = df[df['Diagnosis Name'] == diagnosis_name]
        # region_counts[diagnosis_name] = diagnosis_df['Region Of Origin'].value_counts().head().to_dict()
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



    bmi_ranges = [0, 10, 20, 30, 40, 50, 60, 70, 150]
    bmi_labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70<']

    # Use pandas' cut function to categorize BMI into ranges
    df['BMI Category'] = pd.cut(df['BMI Index'], bins=bmi_ranges, labels=bmi_labels)
    bmi_histogram_dict = {}
    for diagnosis_name, group in df.groupby('Diagnosis Name'):
        # Calculate the BMI index histogram for the current diagnosis
        bmi_histogram = group['BMI Category'].value_counts().sort_index().to_dict()
        bmi_histogram_dict[diagnosis_name] = bmi_histogram
    top_5_diagnoses_dict = top_5_diagnoses.to_dict(orient='records')
    bmi_class = None
    for i, upper_limit in enumerate(bmi_ranges[1:]):
        if bmi_index < upper_limit:
            bmi_class = bmi_labels[i]
            break
    else:
        bmi_class = bmi_labels[-1]
    
    medications_chart_data_json = json.dumps(medication_data_by_diagnosis)
    family_history_by_diagnosis_json = json.dumps(family_history_by_diagnosis)
    past_medical_history = json.dumps(past_medical_history)
    smoker_counts_by_diagnosis_json = json.dumps(smoker_counts_by_diagnosis)
    end_time = datetime.now()
    print("Time taken to execute query:", end_time - start_time)
    region_counts_json = json.dumps(region_counts)

    return render_template('result.html', bmi_histogram_dict=bmi_histogram_dict , result=top_5_diagnoses_dict,time = end_time - start_time,count = total_patients_in_top_5, symptom_data_by_diagnosis=symptom_data_by_diagnosis,
                            region_counts_json=region_counts_json,symptom_data_by_diagnosis_age_range=symptom_data_by_diagnosis_age_range,bmi_class = bmi_class,smoker_counts_by_diagnosis_json= smoker_counts_by_diagnosis_json,
                            gender_chart = sex_chart_data_json, medications_chart_data_ = medications_chart_data_json,past_medical_history = past_medical_history,
                            family_history_by_diagnosis_json=family_history_by_diagnosis_json, region_symptom_data = region_symptom_data, bmi_index = bmi_index)
