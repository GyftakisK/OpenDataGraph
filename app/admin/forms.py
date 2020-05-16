from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, FileField, SelectField)
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired


class LiteratureForm(FlaskForm):
    mesh_term = StringField('MeSH Term', validators=[DataRequired()])
    submit = SubmitField('Add to graph')


class StructuredDrugbankForm(FlaskForm):
    xml_file = FileField(validators=[FileRequired()])
    submit1 = SubmitField('Add to graph')


class StructuredOboForm(FlaskForm):
    obo_file = FileField(validators=[FileRequired()])
    obo_type = SelectField('OBO type', choices=(('do', 'DO'), ('go', 'GO'), ('mesh', 'MeSH')),
                           validators=[DataRequired()])
    submit2 = SubmitField('Add to graph')
