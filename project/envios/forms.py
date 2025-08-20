"""
.. topic:: **Envios (formulários)**

"""

# forms.py na pasta demandas

from flask_wtf import FlaskForm
from wtforms import SubmitField

# form com botão para gerar csv
class CSV_Form(FlaskForm):

    submit = SubmitField('Gerar CSV')


