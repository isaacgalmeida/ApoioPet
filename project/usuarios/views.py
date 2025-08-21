"""
.. topic:: users (views)

    Objetos relativos a usuários
        
.. topic:: Ações relacionadas aos usuários:        

    * login: Login do usuário
    * logout: Logout do usuário

"""
# views.py na pasta users

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime as dt, timedelta
from sqlalchemy import func, distinct, literal, or_
from sqlalchemy.sql import label

import os

from project import db, app
from project.models import Pessoas, Unidades

from project.usuarios.forms import LoginForm, LogForm, RegistrationForm, UserForm

# from cryptography.fernet import Fernet

usuarios = Blueprint('usuarios',__name__)



# login
@usuarios.route('/login', methods=['GET','POST'])
def login():
    """+--------------------------------------------------------------------------------------+
       |Fornece a tela para que o usuário entre no sistema (login).                           |
       |O acesso é feito por usuário e senha cadastrados, conforme ldap.                      |
       +--------------------------------------------------------------------------------------+
    """

    if current_user.is_authenticated:
        flash('Você já estava logado!')
        return redirect(url_for('core.inicio'))

    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        str_conexao     = os.environ.get('STR_CONEXAO')
        str_search      = os.environ.get('STR_SEARCH')
        str_atributo    = os.environ.get('STR_ATRIBUTO')

        # print ('*** str_conexao: ', str_conexao)
        # print ('*** str_search: ', str_search)
        # print ('*** str_atributo: ', str_atributo)

        # abertura para login com usuarios de teste, gatilho para se conseguir logar com usuários que não existem no DIT do LDAP
        # o usuario, contudo, tem que existir na tabela usuario, com o apelido igual ao informado no login
        lista_usuarios = os.environ.get('USER_LIST')
        
        if username in lista_usuarios:
            if password == os.environ.get('USER_LIST_PASS'):
                try:
                    pessoa = Pessoas.query.filter_by(apelido = username).first()
                except Exception as e:
                    print ('** Erro na consulta à tabela usuario **')
                    flash(e,'erro')
                    print (e)

                if not pessoa:
                    flash(username + ' (apelido) não existe na tabela de usuários do banco de dados!', 'erro')
                    return render_template('login.html', form=form)
            else:
                flash('A senha informada não confere com a definida na instalação!', 'erro')
                return render_template('login.html', form=form)          
        else:   

            # conexao = Pessoas.conecta_ldap(username,password,str_conexao) 
            try:
                conexao = Pessoas.conecta_ldap(username,password,str_conexao) 
            except Exception as e:
                flash('Problema no acesso. Por favor, verifique suas credenciais e tente novamente. '+str_conexao+' '+str_search+' '+str_atributo, 'erro')
                flash(e,'erro')
                print(e)
                return render_template('login.html', form=form)

            if conexao == 'sem_credencial':
                retorno = False
                ldap_mail = None
                ldap_cpf  = None
                flash('Usuário desconhecido ou senha inválida. Por favor, tente novamente.', 'erro')
                return render_template('login.html', form=form)
            else:
                #conexao.search('dc=cnpq,dc=br', '(uid='+username+')', attributes=['mail','carLicense'])
                #conexao.search('dc=cnpq,dc=br', '(uid='+username+')', attributes=['mail'])
                conexao.search(str_search, '(uid='+username+')', attributes=[str_atributo])
                retorno = True
                #ldap_mail = str((conexao.entries[0])['mail'])
                ldap_mail = str((conexao.entries[0])[str_atributo])
                #ldap_cpf  = str((conexao.entries[0])['carLicense'])
                pessoa = Pessoas.query.filter_by(email = ldap_mail).first()
                if not pessoa:
                    flash('Seu e-mail no PGD não bate com sei e-mail no LDAP ('+ldap_mail+') ou você não está cadastrato lá. Acesso negado!','erro')
                    return render_template('login.html', form=form)
            
        login_user(pessoa)

        # flash('Login bem sucedido!','sucesso')

        next = request.args.get('next')

        if next == None or not next[0] == '/':
            next = url_for('core.inicio')

        return redirect(next)

    return render_template('login.html',form=form)

# logout
@usuarios.route('/logout')
def logout():
    """+--------------------------------------------------------------------------------------+
       |Efetua a saída do usuário do sistema.                                                 |
       +--------------------------------------------------------------------------------------+
    """
    
    # registra_log_gestao(current_user.pessoaId,'Pessoa "'+ current_user.pesNome +'" efetuou logout.')
    
    logout_user()

    return redirect(url_for("core.index"))

