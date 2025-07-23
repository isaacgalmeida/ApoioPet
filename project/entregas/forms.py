"""
.. topic:: **entregas (formulários)**

    Os formulários do módulo *entregas* recebem dados informados pelo usuário para
    registro, atualização de programas de gestão.

    * PGForm: iserir ou alterar pg.

"""

# forms.py na pasta objetos

import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields.html5 import DateField                    
from wtforms.validators import DataRequired, Optional


class PEForm(FlaskForm):

    instituidora = SelectField('Instituidora', validators=(Optional(),))
    unidade      = SelectField('Executora', validators=(Optional(),))
    data_ini     = DateField('Data início', format='%Y-%m-%d', validators=[DataRequired(message="Informe data de início!")])
    data_fim     = DateField('Data fim', format='%Y-%m-%d', validators=[DataRequired(message="Informe data de fim!")])
    # tempo_comp   = IntegerField('T.C.',validators=[DataRequired(message="Insira o tempo para comparecimento!")])
    # qtd_colab    = IntegerField('Qtd Colab.',validators=[DataRequired(message="Insira a quantidade de colaboradores!")])
    situ         = SelectField('Situação', validators=(Optional(),))
    planejamento = SelectField('Planejamento', validators=(Optional(),))
    
    # termo_aceite = TextAreaField('Termo de aceite', validators=(Optional(),))

    submit       = SubmitField('Registrar')  
    
