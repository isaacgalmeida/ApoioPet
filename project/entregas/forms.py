"""

.. topic:: Entregas (formulários)

   Formulários de Planos de entregas.


"""

from flask_wtf import FlaskForm
from wtforms import SubmitField

# form com botão para gerar csv
class CSV_Form(FlaskForm):

    submit = SubmitField('Gerar CSV') 