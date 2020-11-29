from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, FileField, SelectField)
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired, FileAllowed


class LiteratureForm(FlaskForm):
    mesh_term = StringField('MeSH Term', validators=[DataRequired()])
    submit1 = SubmitField('Add to graph')


class StructuredDrugbankForm(FlaskForm):
    xml_file = FileField('Drugbank XML file', validators=[FileRequired()])
    version = StringField('Version', validators=[DataRequired()])
    submit2 = SubmitField('Add to graph')


class StructuredOboForm(FlaskForm):
    obo_file = FileField('OBO file', validators=[FileRequired()])
    version = StringField('Version', validators=[DataRequired()])
    obo_type = SelectField('OBO type', choices=(('do', 'DO'), ('go', 'GO'), ('mesh', 'MeSH')),
                           validators=[DataRequired()])
    submit3 = SubmitField('Add to graph')
