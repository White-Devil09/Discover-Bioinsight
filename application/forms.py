from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, TextAreaField, SelectField 
from wtforms.validators import DataRequired

class PatientForm(FlaskForm):
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField("Gender",choices=[("Male","Male"),("Female","Female"),("Other","Other")],default="Male",validators=[DataRequired()])
    region_of_origin = SelectField("Region of Origin",choices=[("North","North"),("South","South"),("East","East"),("West","West")],default="North",validators=[DataRequired()])
    cholestrol = IntegerField('Cholestrol', validators=[DataRequired()])
    Weight = IntegerField('Weight', validators=[DataRequired()])
    Height = IntegerField('Height', validators=[DataRequired()])
    symptoms = TextAreaField('Symptoms', validators=[DataRequired()])
    medication = TextAreaField('Medication', validators=[DataRequired()])
    pastmedical_history = TextAreaField('Past Medical History', validators=[DataRequired()])
    alcohol = SelectField("Alcohol",choices=[("Yes","Yes"),("No","No")],default="No",validators=[DataRequired()])
    smoking = SelectField("Smoking",choices=[("Yes","Yes"),("No","No")],default="No",validators=[DataRequired()])
    diabetic = SelectField("Diabetic",choices=[("Yes","Yes"),("No","No")],default="No",validators=[DataRequired()])
    family_history = TextAreaField('Family History', validators=[DataRequired()])
    final_diagnosis = TextAreaField('Final Diagnosis', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    submit = SubmitField('Submit')