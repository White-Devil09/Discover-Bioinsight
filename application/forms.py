from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, TextAreaField 
from wtforms.validators import DataRequired

class PatientForm(FlaskForm):
    Weight = IntegerField('Weight', validators=[DataRequired()])
    Height = IntegerField('Height', validators=[DataRequired()])
    symptoms = TextAreaField('Symptoms', validators=[DataRequired()])
    medication = TextAreaField('Medication', validators=[DataRequired()])
    pastmedical_history = TextAreaField('Past Medical History', validators=[DataRequired()])
    family_history = TextAreaField('Family History', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    submit = SubmitField('Submit')