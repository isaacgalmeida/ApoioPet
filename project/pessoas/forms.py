"""
.. topic:: **pessoas (formulários)**

    Os formulários do módulo *pessoas*.

    * PesquisaForm: Encontrar uma pessoa mediante pesquisa

"""

# forms.py na pasta pessoas

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField

class PesquisaForm(FlaskForm):

   nome    = StringField('Nome:')
   unidade = SelectField('Unidade:')
   situ    = SelectField('Situação:')
   atrib   = SelectField('Atribuição:')
   perf    = SelectField('Perfil:')
   
   submit  = SubmitField('Pesquisar')

# form com botão para gerar csv
class CSV_Form(FlaskForm):

    submit2 = SubmitField('Gerar CSV')   
   

        