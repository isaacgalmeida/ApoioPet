"""
.. topic:: entregas (views)

    Planos de Entregas.

"""

# views.py dentro da pasta entregas

from flask import render_template, url_for, flash, redirect, Blueprint
from flask_login import current_user, login_required
from sqlalchemy import func, case, literal_column, or_, distinct
from sqlalchemy.sql import label
from sqlalchemy.orm import aliased
from project import db, app
from project.models import Unidades, Pessoas, programas, planos_entregas, unidades_integrantes,\
                           avaliacoes, planos_entregas_entregas, planos_trabalhos_entregas, tipos_modalidades, planos_trabalhos_consolidacoes,\
                           planos_trabalhos, PlanoTrabalhoTrabalhos

from project.entregas.forms import PEForm             

from project.usuarios.views import registra_log_unid                       

from datetime import datetime as dt

import uuid


entregas = Blueprint("entregas",__name__,template_folder='templates')    


## lista planos de entregas

@entregas.route('/lista_pe')
@login_required
def lista_pe():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta os planos de entregas.                                                       |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """
        
    unid_dados = db.session.query(Unidades.id, Unidades.sigla, Unidades.path)\
                            .all()

    entregas = db.session.query(planos_entregas_entregas.plano_entrega_id,
                                label('qtd_entregas',func.count(planos_entregas_entregas.id)))\
                         .group_by(planos_entregas_entregas.plano_entrega_id)\
                         .subquery()                                               
                            
    pts_todos_1 = db.session.query(label('pt_id',planos_trabalhos_entregas.plano_trabalho_id.distinct()),
                                   planos_trabalhos_entregas.plano_entrega_entrega_id,
                                   planos_entregas_entregas.plano_entrega_id)\
                            .join(planos_entregas_entregas, planos_entregas_entregas.id == planos_trabalhos_entregas.plano_entrega_entrega_id)\
                            .subquery()
    planos_trab = db.session.query(label('pe_id',pts_todos_1.c.plano_entrega_id.distinct()),
                                   label('qtd_planos_trab',func.count(distinct(pts_todos_1.c.pt_id))))\
                            .group_by(pts_todos_1.c.plano_entrega_id)\
                            .subquery()                      
                                                                                      
                            
    unidades_pai = aliased(Unidades)                                                                          


    hoje = dt.now()
        
    planos_entregas_todos = db.session.query(planos_entregas.id,
                                       planos_entregas.status,
                                       planos_entregas.data_inicio,
                                       planos_entregas.data_fim,
                                       planos_entregas.deleted_at,
                                       entregas.c.qtd_entregas,
                                       planos_trab.c.qtd_planos_trab,
                                       Unidades.sigla,
                                       label('sigla_pai', unidades_pai.sigla),
                                       planos_entregas.unidade_id,
                                       Unidades.unidade_pai_id,
                                       label('vencido',case((planos_entregas.data_fim < hoje, literal_column("'s'")), else_=literal_column("'n'"))),
                                       avaliacoes.nota,
                                       avaliacoes.data_avaliacao,
                                       label('just_avalia',avaliacoes.justificativas),
                                       label('parecer_avalia',avaliacoes.justificativa))\
                                .join(Unidades, Unidades.id == planos_entregas.unidade_id)\
                                .outerjoin(unidades_pai, unidades_pai.id == Unidades.unidade_pai_id)\
                                .outerjoin(entregas, entregas.c.plano_entrega_id == planos_entregas.id)\
                                .outerjoin(planos_trab,planos_trab.c.pe_id == planos_entregas.id)\
                                .outerjoin(avaliacoes,avaliacoes.plano_entrega_id == planos_entregas.id)\
                                .filter(planos_entregas.deleted_at == None)\
                                .order_by(planos_entregas.status, Unidades.sigla, planos_entregas.data_inicio)\
                                .all() 
                               

    quantidade = len(planos_entregas_todos)
            

    return render_template('lista_pe.html', unid_dados = unid_dados,
                                            planos_entregas_todos = planos_entregas_todos,
                                            quantidade = quantidade)


## consulta entregas de um plano de entregas

@entregas.route('/<peId>/consulta_entregas')
@login_required
def consulta_entregas(peId):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das entregas de um Plano de Entergas.                              |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """   
    
    plano_entregas = db.session.query(planos_entregas.status,
                                      planos_entregas.data_inicio,
                                      planos_entregas.data_fim, 
                                      Unidades.sigla)\
                               .join(Unidades, Unidades.id == planos_entregas.unidade_id)\
                               .filter(planos_entregas.id == peId).first()
    
    entregas = db.session.query(planos_entregas_entregas).filter(planos_entregas_entregas.plano_entrega_id == peId).all()
    
    
    quantidade = len(entregas)
    
    return render_template("consulta_entregas.html", plano_entregas =plano_entregas, 
                                                     entregas = entregas,
                                                     quantidade = quantidade)
    
    
## lista planos de trabalho vinculados a um plano de entregas

@entregas.route('/<peId>/consulta_pts')
@login_required
def consulta_pts(peId):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista de planos de trabalho vinculados a um plano de entregas.           |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """   

    hoje = dt.today().date()
    
    pe = db.session.query(planos_entregas.status,
                          planos_entregas.data_inicio,
                          planos_entregas.data_fim, 
                          Unidades.sigla)\
                   .join(Unidades, Unidades.id == planos_entregas.unidade_id)\
                   .filter(planos_entregas.id == peId).first()
                         

    #subquery que conta avaliações realizadas até em cada pt (exclui as autormáticas futuras)
    avaliacoes_pt = db.session.query(planos_trabalhos_consolidacoes.plano_trabalho_id,
                                     label('qtd_aval',func.count(avaliacoes.id)))\
                              .join(planos_trabalhos_consolidacoes, planos_trabalhos_consolidacoes.id == avaliacoes.plano_trabalho_consolidacao_id)\
                              .group_by(planos_trabalhos_consolidacoes.plano_trabalho_id)\
                              .subquery()                                            
    
    
    planos_trab_pe  = db.session.query(planos_trabalhos.id.distinct(),
                                       planos_trabalhos.data_inicio,
                                       planos_trabalhos.data_fim,
                                       planos_trabalhos.carga_horaria,
                                       planos_trabalhos.forma_contagem_carga_horaria,
                                       planos_trabalhos.status,
                                       planos_trabalhos.tempo_total,
                                       planos_trabalhos.tempo_proporcional,
                                       planos_trabalhos_entregas.plano_trabalho_id,
                                       planos_entregas_entregas.plano_entrega_id,
                                       Pessoas.nome,
                                       Unidades.sigla,
                                       label('forma',tipos_modalidades.nome),
                                       avaliacoes_pt.c.qtd_aval)\
                                .filter(planos_entregas_entregas.plano_entrega_id == peId)\
                                .join(Pessoas, Pessoas.id == planos_trabalhos.usuario_id)\
                                .join(planos_trabalhos_entregas, planos_trabalhos_entregas.plano_trabalho_id == planos_trabalhos.id)\
                                .join(planos_entregas_entregas, planos_entregas_entregas.id == planos_trabalhos_entregas.plano_entrega_entrega_id)\
                                .join(Unidades, Unidades.id == planos_trabalhos.unidade_id)\
                                .join(tipos_modalidades, tipos_modalidades.id == planos_trabalhos.tipo_modalidade_id)\
                                .outerjoin(avaliacoes_pt,avaliacoes_pt.c.plano_trabalho_id == planos_trabalhos.id,)\
                                .order_by(Pessoas.nome)\
                                .all()    

    quantidade = len(planos_trab_pe)


    return render_template('consulta_pts.html', pe = pe, 
                                                quantidade = quantidade,
                                                planos_trab_pe = planos_trab_pe)                                                



# ver dados de um plano de entregas
@entregas.route('/<peId>/ver_pe', methods=['GET','POST'])
@login_required
def ver_pe(peId):
    """
    +---------------------------------------------------------------------------------------+
    |Visualizar/alterar dados de um Plano de Entregas.                                      |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """
    
    tipo = 'alt'

    hoje = dt.now()
    
    pe_consulta = db.session.query(PlanoEntregas).filter(PlanoEntregas.planoEntregasId == peId).first()
    
    pe_consulta_vw = db.session.query(VW_PlanoEntregas).filter(VW_PlanoEntregas.id_plano_entrega_unidade == peId).first()
    
    executora = VW_Unidades.query.filter_by(unidadeId = pe_consulta.unidadeId).first()
    instituidora = VW_Unidades.query.filter_by(unidadeId = pe_consulta.instituidoraId).first()
    
    planejamento = Planejamento.query.filter_by(planejamentoId = pe_consulta.planejamentoId).first()

    #quantidade de entregas do PE
    entregas_qtd = db.session.query(PlanoEntregasEntregas).filter(PlanoEntregasEntregas.planoEntregasId == peId).count()

    #pega total de servidores do setor
    # total_serv_setor = db.session.query(Pessoas).filter(Pessoas.pesEmail == current_user.pesEmail).count()
    
    #monta estrutura superior da executora, incluindo a executora
    unids_super = executora.undSiglaCompleta.split('/')
    lista_super = [(u.unidadeId, u.undSigla) for u in Unidades.query.filter(Unidades.undSigla.in_(unids_super))]
    lista_super_ids = [u[0] for u in lista_super]
    
    #monta subestrutura da executora, incluindo a executora
    pai = [executora.unidadeId]
    lista_infra = [(executora.unidadeId, executora.undSigla)]

    while pai != []:
        
        prox_pai = []
        
        for p in pai:

            filhos = Unidades.query.filter(Unidades.unidadeIdPai==p).all()
            
            for f in filhos:
                
                prox_pai.append(f.unidadeId)
                
                lista_infra.append((f.unidadeId,f.undSigla)) 
                
        pai =  prox_pai
 

    form = PEForm()
    
    #choices do campo executora e campo instituidora
    form.unidade.choices = lista_infra
    form.instituidora.choices = lista_super
    
    pode_deletar = False
    pode_alterar_data = False
    
    # limita situações que o usuário pode colocar para o PE
    
    # o usuário logado não é de unidade superior à executora do PE
    if current_user.unidadeId not in lista_super_ids: 
            
        # a opção disponível é a opção atual do plano        
        situ_planos_entregas = db.session.query(catdom)\
                                         .filter(catdom.catalogoDominioId == pe_consulta.situacaoId).all()
        lista_situ = [(s.catalogoDominioId,s.descricao) for s in situ_planos_entregas] 
        form.situ.choices = lista_situ
        
        pode_deletar = False
        pode_alterar_data = False
            
    # o usuário é da mesma unidade do PE
    elif current_user.unidadeId == pe_consulta.unidadeId:
        # a opção é concluído
        situ_planos_entregas = db.session.query(catdom)\
                                         .filter(catdom.classificacao == 'SituacaoPlanoEntregas',
                                                 catdom.ativo,
                                                 catdom.catalogoDominioId != 301,
                                                 catdom.catalogoDominioId != 302,
                                                 catdom.catalogoDominioId != 309,
                                                 catdom.catalogoDominioId != 312,
                                                 catdom.catalogoDominioId != 313,
                                                 catdom.catalogoDominioId != 314).all()
        lista_situ = [(s.catalogoDominioId,s.descricao) for s in situ_planos_entregas]
        lista_situ.insert(0,('',''))
        form.situ.choices = lista_situ
        
        pode_deletar = False
        pode_alterar_data = False
        
    # o usuário logado é de uma unidade superior à do PE
    else:
        # as opções são todas as situação, menos enviados
        if entregas_qtd > 0:
            situ_planos_entregas = db.session.query(catdom)\
                                            .filter(catdom.classificacao == 'SituacaoPlanoEntregas',
                                                    catdom.ativo,
                                                    catdom.catalogoDominioId != 302,
                                                    catdom.catalogoDominioId != 313,
                                                    catdom.catalogoDominioId != 314).all()
        # se não tiver entregas, só pode indeferir ou colocar em rascunho
        else:
            situ_planos_entregas = db.session.query(catdom)\
                                            .filter(catdom.classificacao == 'SituacaoPlanoEntregas',
                                                    catdom.ativo,
                                                    catdom.catalogoDominioId != 302,
                                                    catdom.catalogoDominioId != 309,
                                                    catdom.catalogoDominioId != 310,
                                                    catdom.catalogoDominioId != 313,
                                                    catdom.catalogoDominioId != 314).all()                                            
        lista_situ = [(s.catalogoDominioId,s.descricao) for s in situ_planos_entregas]
        lista_situ.insert(0,('',''))
        form.situ.choices = lista_situ
        
        pode_deletar = True
        pode_alterar_data = True
    
    
    if form.validate_on_submit():
        
        # verifica se há planos (ou aprovado, ou concluído, ou modificado) cuja vigência contém o início do plano proposto
        plano_data_conflitante = db.session.query(PlanoEntregas)\
                                          .filter(PlanoEntregas.unidadeId  == executora.unidadeId,
                                                  PlanoEntregas.dataFim  >= form.data_ini.data,
                                                  PlanoEntregas.dataInicio <= form.data_fim.data,
                                                  PlanoEntregas.planoEntregasId != pe_consulta.planoEntregasId,
                                                  or_(PlanoEntregas.situacaoId == 302,
                                                      PlanoEntregas.situacaoId == 309,
                                                      PlanoEntregas.situacaoId == 313,
                                                      PlanoEntregas.situacaoId == 310,
                                                      PlanoEntregas.situacaoId == 314))\
                                          .first()
        if plano_data_conflitante != None:
            flash('Plano de Entregas não foi alterado! O período informado tem conflito com outro plano preexistente.','erro')
            return redirect(url_for('entregas.ver_pe',peId=peId)) 

        
        if pe_consulta_vw != None and pe_consulta_vw.data_avaliacao_plano_entregas != None and form.data_ini.data > pe_consulta_vw.data_avaliacao_plano_entregas:
            flash('Data de início inválida, pois é maior do que a data de avaliação registrada: '\
                  +pe_consulta_vw.data_avaliacao_plano_entregas.strftime('%d/%m/%Y')+'.', 'erro')
            return redirect(url_for('entregas.ver_pe',peId=peId))
        
        #altera registro do PlanoEntregas consultado, somente se altuma coisa tiver sido alterada mesmo
        situ_atual = pe_consulta.situacaoId
        alterado = False

        if pe_consulta.dataInicio != form.data_ini.data:
            pe_consulta.dataInicio = form.data_ini.data
            pe_consulta.situacaoId  = 302
            alterado = True
        if pe_consulta.dataFim != form.data_fim.data: 
            pe_consulta.dataFim = form.data_fim.data
            pe_consulta.situacaoId  = 302
            alterado = True
        
        if form.situ.data != '' and situ_atual != int(form.situ.data):
            pe_consulta.situacaoId = int(form.situ.data)
            alterado = True

        if alterado == True:    

            #cria registro em PlanoEntregasHistorico
            hist = PlanoEntregasHistorico(planoEntregasHistoricoId = uuid.uuid4(),
                                        planoEntregasId          = pe_consulta.planoEntregasId,
                                        situacaoId               = pe_consulta.situacaoId,
                                        observacoes              = 'Atualizando Plano de Entregas.',
                                        responsavelOperacao      = current_user.pessoaId,
                                        DataOperacao             = hoje)

            db.session.add(hist)
            
            # se o PE consta como enviado, coloca como apto ao envio
            enviar = False
            if pe_consulta.situacaoId == 313:
                pe_consulta.situacaoId = 309
                enviar = True
            elif pe_consulta.situacaoId == 314:
                pe_consulta.situacaoId = 310
                enviar = True

            db.session.commit()
            
            registra_log_unid(current_user.pessoaId,'Plano de Entregas '+ pe_consulta.planoEntregasId +' atualizado.')      
            flash('Plano de Entregas atualizado.','sucesso')     
            
            # dispara envia_API no caso de acumulados atingirem o limite
            if enviar:
                thread_envia_acumulado('pe')                      

            return redirect(url_for('entregas.lista_pe'))
    
    form.data_ini.data = pe_consulta.dataInicio
    form.data_fim.data = pe_consulta.dataFim
    if str(pe_consulta.situacaoId) == '313':
        form.situ.data = '309'
    elif str(pe_consulta.situacaoId) == '314':
        form.situ.data = '310' 
    else:   
        form.situ.data = str(pe_consulta.situacaoId)

    situ_atual = catdom.query.filter_by(catalogoDominioId = pe_consulta.situacaoId).first()  
    
    
    return render_template('add_pe.html',form=form, 
                                         tipo=tipo, 
                                         unidade = executora, 
                                         instituidora = instituidora,
                                         pode_deletar = pode_deletar, 
                                         pode_alterar_data = pode_alterar_data,
                                         peId = peId,
                                         pe_consulta = pe_consulta,
                                         planejamento = planejamento,
                                         situ_atual = situ_atual.descricao,
                                         entregas_qtd = entregas_qtd)



