"""
.. topic:: Core (views)

    Este é o módulo inicial do sistema.

    Apresenta as telas de início, informação e procedimentos genéricos do sistema.

.. topic:: Ações relacionadas ao Core

    * Funções:
        PegaArquivo   
    
    * index: Tela inicial. Pede o login do usuário.
    * inicio: Rotinas executadas quando se entra no aplicativo.
    * info: informações do sistema.
    * internas_i: abre tela de menu das funções internas
    * apoio_i: abre tela de menu das funções de apoio
    * cargas_i: abre tela de menu das cargas
    

"""

# core/views.py

from flask import render_template,url_for,flash, redirect, request, Blueprint, send_from_directory

import os
from datetime import datetime as dt
import tempfile
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from sqlalchemy import distinct, or_
from sqlalchemy.sql import label

from project import db

from project.models import Unidades

from project.core.forms import ArquivoForm

from project.usuarios.views import registra_log_unid


core = Blueprint("core",__name__)

## função para pegar arquivo

def PegaArquivo(form):

    '''
        DOCSTRING: solicita arquivo do usuário e salva em diretório temporário para ser utilizado
        INPUT: formulário de entrada
        OUTPUT: arquivo de trabalho
    '''

    tempdirectory = tempfile.gettempdir()

    f = form.arquivo.data
    fname = secure_filename(f.filename)
    arquivo = os.path.join(tempdirectory, fname)
    f.save(arquivo)

    print ('***  ARQUIVO ***',arquivo)

    pasta = os.path.normpath(tempdirectory)

    if not os.path.exists(pasta):
        os.makedirs(os.path.normpath(pasta))

    arq = fname
    arq = os.path.normpath(pasta+'/'+arq)

    return arq

@core.route('/')
def index():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta a tela de login.                                                             |
    +---------------------------------------------------------------------------------------+
    """

    return redirect(url_for('usuarios.login'))

@core.route('/inicio')
def inicio():
    
    """
    +---------------------------------------------------------------------------------------+
    |Ações quando o aplicativo é colocado no ar.                                            |
    |Inicia jobs de envio e de reenvio conforme ultimo registro de agendamento no log.      |
    +---------------------------------------------------------------------------------------+
    """
        
    return render_template ('index.html')  

@core.route('/info')
def info():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta a tela de informações do aplicativo.                                         |
    +---------------------------------------------------------------------------------------+
    """

    return render_template('info.html')

@core.route('/v_a')
def v_a():
    """
    +---------------------------------------------------------------------------------------+
    |Lista variáveis de ambiente.                                                           |
    +---------------------------------------------------------------------------------------+
    """

    return render_template('v_a.html')



