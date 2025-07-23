"""

.. topic:: **Usuários (formulários)**

   Os formulários do módulo *Users*.

   Para o tratamento de usuários, foram definidos os seguintes:

   * LoginForm: utilizado para entrar (login) no sistema.
   * LogForm: para que o usuário informe o intervalo de datas para resgatar registros do log
   * AgendaForm: agendar o comparecimento de uma pessoa


"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.fields.html5 import DateField                    
from wtforms.validators import DataRequired, Optional
from wtforms import ValidationError
from flask import flash

from flask_login import current_user

class LoginForm(FlaskForm):

    username = StringField('Usuário: ', validators=[DataRequired(message="Informe Usuário!")])
    password = PasswordField('Senha: ', validators=[DataRequired(message="Informe sua senha!")])
    submit   = SubmitField('Entrar')

class LogForm(FlaskForm):

    data_ini = DateField('Data Inicial: ', format='%Y-%m-%d')
    data_fim = DateField('Data Final: ', format='%Y-%m-%d')

    submit   = SubmitField('Procurar') 
    
class RegistrationForm(FlaskForm):

    pessoa      = SelectField('Pessoa', validators=[DataRequired(message="Escolha a pessoa!")],coerce=int)
    # user_api    = StringField('User API', validators=[DataRequired(message="Informe credencial de acesso à API!")])
    # senha_api   = StringField('Senha API', validators=[DataRequired(message="Informe a senha da credencial de acesso à API!")])
    # instituicao = SelectField('Instituidora',validators=[DataRequired(message="Escolha a Instituidora!")],coerce=int)
    
    submit      = SubmitField('Registrar') 
    
class UserForm(FlaskForm):

    pessoa      = SelectField('Pessoa', validators=(Optional(),))
    # user_api    = StringField('User API', validators=[DataRequired(message="Informe credencial de acesso à API!")])
    # senha_api   = StringField('Senha API', validators=[DataRequired(message="Informe a senha da credencial de acesso à API!")])
    # instituicao = SelectField('Instituidora:', validators=[DataRequired(message="Escolha a instituição!")],coerce=int)
    
    submit = SubmitField('Atualizar')
