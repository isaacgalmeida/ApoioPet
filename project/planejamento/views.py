"""
.. topic:: Planejamento (views)

    Sobre o Planejamento Institucional.


.. topic:: Ações relacionadas às pessoas

    * mapa_estratégico: Mostra o Mapa Estratégico

"""

# views.py na pasta planejamento

from flask import render_template, Blueprint
from flask_login import current_user, login_required

from sqlalchemy.sql import label

from project import db
from project.models import planejamentos, Unidades, planejamentos_objetivos, eixos_tematicos
                            
from datetime import datetime as dt

import ast, json

planejamento = Blueprint('planejamento',__name__, template_folder='templates')

hoje = dt.today().date()


## mapa estratégico

@planejamento.route('/mapa_estrategico')
@login_required
def mapa_estrategico():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta o mapa estratégico da instituição.                                           |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """ 
        
    # pega instituição
    
    # pega primeiro planejamento vigente
    planejamento_inst = db.session.query(planejamentos.id,
                                         planejamentos.nome,
                                         planejamentos.missao,
                                         planejamentos.visao,
                                         planejamentos.data_inicio,
                                         planejamentos.data_fim,
                                         Unidades.sigla,
                                         planejamentos.valores,
                                         planejamentos.resultados_institucionais)\
                                  .join(Unidades, Unidades.id == planejamentos.unidade_id)\
                                  .filter(planejamentos.deleted_at == None,
                                          planejamentos.data_inicio <= hoje,
                                          planejamentos.data_fim >= hoje)\
                                  .first()
    
    #pega valores
    valores = planejamento_inst.valores
    # lista_valores = ast.literal_eval(valores)
    
    #pega resultados
    resultados = planejamento_inst.resultados_institucionais
    # lista_resultados = ast.literal_eval(resultados) 
                            
    # pega objetivos por eixo temático
    
    objetivos = db.session.query(planejamentos_objetivos.id,
                                 planejamentos_objetivos.planejamento_id,
                                 planejamentos_objetivos.nome,
                                 planejamentos_objetivos.fundamentacao,
                                 planejamentos_objetivos.eixo_tematico_id,
                                 label('eixo_nome',eixos_tematicos.nome),
                                 label('eixo_cor',eixos_tematicos.cor),
                                 label('eixo_desc',eixos_tematicos.descricao))\
                          .join(eixos_tematicos, eixos_tematicos.id == planejamentos_objetivos.eixo_tematico_id)\
                          .filter(planejamentos_objetivos.planejamento_id == planejamento_inst.id)\
                          .order_by(planejamentos_objetivos.nome)\
                          .all()  
                           
    lista_eixo = set([(o.eixo_nome, o.eixo_desc, o.eixo_cor) for o in objetivos])
                        
    
    return render_template('mapa_estrategico.html', planejamento = planejamento_inst,
                                                    valores = valores,
                                                    resultados = resultados,
                                                    objetivos = objetivos, 
                                                    lista_eixo = lista_eixo)                    
    
     
   
 