"""

.. topic:: Unidades (formulários)

   Formulários de unidades da instituição.

   * PesquisaUnidForm: busca unidades conforme filtro aplicado.

"""

# forms.py dentro de convenios

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField

class PesquisaUnidForm(FlaskForm):

   sigla = SelectField('Sigla:')
   nome  = StringField('Nome:')
   pai   = SelectField('Pai:')
   uf    = StringField('UF:')
   
   submit = SubmitField('Pesquisar')

# form com botão para gerar csv
class CSV_Form(FlaskForm):

    submit = SubmitField('Gerar CSV') 