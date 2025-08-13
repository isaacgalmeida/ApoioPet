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

from flask import render_template,url_for, redirect, Blueprint

core = Blueprint("core",__name__)

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



