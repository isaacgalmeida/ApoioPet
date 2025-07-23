"""
.. topic:: Pessoas (views)

    As Pessoas são os servidores lotados na intituição.
    
.. topic:: Ações relacionadas à gestão de pessoas

    * lista_pessoas: Lista das pessoas da instituição
    * lista_pessoas_filtro: Procura pessoas na instituição 

"""

# views.py na pasta pessoas

from flask import render_template, Blueprint, request
from flask_login import current_user, login_required

from sqlalchemy.sql import label
from sqlalchemy import func, distinct

from project import db
from project.models import Unidades, unidades_integrantes, Pessoas, perfis, unidades_integrantes_atribuicoes, planos_trabalhos,\
                           planos_trabalhos_entregas, planos_entregas_entregas, tipos_modalidades, planos_trabalhos_consolidacoes,\
                           avaliacoes
                            
from project.pessoas.forms import PesquisaForm


pessoas = Blueprint('pessoas',__name__, template_folder='templates')


 ## lista pessoas da instituição

@pessoas.route('/lista_pessoas')
@login_required

def lista_pessoas():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das pessoas da instituição.                                        |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """

    page = request.args.get('page', 1, type=int)    

    tipo = "inst"
    
    # Verifica a quantidade de pessoas para decidir sobre paginação
    
    qtd_pessoas = db.session.query(Pessoas).count()
        
    if qtd_pessoas < 500:
        pag = 500
    else:
        pag = 100
    
    # Lê tabela pessoas

    pessoas_lista = db.session.query(Pessoas.id,
                                     Pessoas.nome,
                                     Pessoas.cpf,
                                     Pessoas.data_nascimento,
                                     Pessoas.matricula,
                                     Pessoas.email,
                                     Unidades.sigla,
                                     unidades_integrantes_atribuicoes.atribuicao,
                                     Pessoas.situacao_funcional,
                                     label('perfil',perfis.nome),
                                     label('qtd_planos_trab',func.count(distinct(planos_trabalhos.id))))\
                                .outerjoin(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                .outerjoin(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                .outerjoin(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                                .join(perfis, perfis.id == Pessoas.perfil_id)\
                                .outerjoin(planos_trabalhos, planos_trabalhos.usuario_id == Pessoas.id)\
                                .filter(Pessoas.deleted_at == None)\
                                .order_by(Pessoas.nome)\
                                .group_by(Pessoas.id,Unidades.sigla,unidades_integrantes_atribuicoes.atribuicao)\
                                .paginate(page=page,per_page=pag)

    quantidade = pessoas_lista.total


    return render_template('lista_pessoas_gestor.html', pessoas = pessoas_lista,
                                                        quantidade = quantidade,
                                                        qtd_pessoas = qtd_pessoas,
                                                        tipo = tipo)
    
    
## lista pessoas da instituição conforme filtro aplicado

@pessoas.route('/lista_pessoas_filtro', methods=['GET','POST'])
@login_required

def lista_pessoas_filtro():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das pessoas da instituição via filtro                              |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """

    page = request.args.get('page', 1, type=int)
    
    pag = 100

    tipo = "pesq"

    form = PesquisaForm()     
    
    unids = db.session.query(Unidades.id,Unidades.sigla)\
                      .filter(Unidades.deleted_at == None)\
                      .order_by(Unidades.sigla).all()
    lista_unids = [(u.id,u.sigla) for u in unids]
    lista_unids.insert(0,('','Todas'))         

    perf = db.session.query(perfis.id, perfis.nome).order_by(perfis.nome).all()
    lista_perf = [(p.id,p.nome) for p in perf]
    lista_perf.insert(0,('','Todos'))
    
    situ = db.session.query(label('situ',Pessoas.situacao_funcional.distinct()))\
                     .order_by(Pessoas.situacao_funcional).all()
    lista_situ = [(s.situ,s.situ) for s in situ]
    lista_situ.insert(0,('','Todas'))

    atrib = db.session.query(label('atrib',unidades_integrantes_atribuicoes.atribuicao.distinct()))\
                      .order_by(unidades_integrantes_atribuicoes.atribuicao).all()
    lista_atrib = [(a.atrib,a.atrib) for a in atrib]
    lista_atrib.insert(0,('','Todas'))

    form.perf.choices    = lista_perf
    form.situ.choices    = lista_situ
    form.atrib.choices   = lista_atrib
    form.unidade.choices = lista_unids

    if form.validate_on_submit():

        if form.situ.data == '':
            p_situ_pattern = '%'
        else:
            p_situ_pattern = '%'+form.situ.data+'%'

        if form.perf.data == '':
            p_perf_pattern = '%'
        else:
            p_perf_pattern = '%'+form.perf.data+'%'
            
        if form.atrib.data == '':
            p_atrib_pattern = '%'
        else:
            p_atrib_pattern = form.atrib.data
            
        if form.unidade.data == '':
            p_unid_pattern = '%'
        else:
            p_unid_pattern = '%'+form.unidade.data+'%'       

        # pega valores utilizados como filtro para exibição na tela da lista
        p_situ  = dict(form.situ.choices).get(form.situ.data)
        p_unid  = dict(form.unidade.choices).get(form.unidade.data) 
        p_perf  = dict(form.perf.choices).get(form.perf.data) 
        p_atrib = dict(form.atrib.choices).get(form.atrib.data) 

        pessoas_lista = db.session.query(Pessoas.id,
                                         Pessoas.nome,
                                         Pessoas.cpf,
                                         Pessoas.data_nascimento,
                                         Pessoas.matricula,
                                         Pessoas.email,
                                         Unidades.sigla,
                                         unidades_integrantes_atribuicoes.atribuicao,
                                         Pessoas.situacao_funcional,
                                         label('perfil',perfis.nome),
                                         label('perfil_id',perfis.id),
                                         label('qtd_planos_trab',func.count(distinct(planos_trabalhos.id))))\
                                  .outerjoin(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                  .outerjoin(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                  .outerjoin(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                                  .join(perfis, perfis.id == Pessoas.perfil_id)\
                                  .outerjoin(planos_trabalhos, planos_trabalhos.usuario_id == Pessoas.id)\
                                  .filter(Pessoas.deleted_at == None,
                                          Pessoas.nome.like('%'+form.nome.data+'%'),
                                          Unidades.id.like(p_unid_pattern),
                                          Pessoas.situacao_funcional.like(p_situ_pattern),
                                          perfis.id.like(p_perf_pattern),
                                          unidades_integrantes_atribuicoes.atribuicao.like(p_atrib_pattern))\
                                  .order_by(Pessoas.nome)\
                                  .group_by(Pessoas.id,Unidades.sigla,unidades_integrantes_atribuicoes.atribuicao)\
                                  .paginate(page=page,per_page=pag)
    
        quantidade = pessoas_lista.total


        return render_template('lista_pessoas_gestor.html', pessoas = pessoas_lista, quantidade=quantidade,
                                                            tipo = tipo,
                                                            p_atrib = p_atrib, p_perf = p_perf,
                                                            p_situ = p_situ, p_unid = p_unid, p_nome = form.nome.data)

    return render_template('pesquisa_pessoas.html', form = form)                                                

     
## lista planos de trabalho vinculados a uma pessoa

@pessoas.route('/<pessoa_id>/consulta_pts_pessoa')
@login_required
def consulta_pts_pessoa(pessoa_id):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista de planos de trabalho vinculados a uma pessoa.                     |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """   
                         
    dados_pessoa = db.session.query(Pessoas.nome).filter(Pessoas.id == pessoa_id).first()
    
    #subquery que conta avaliações realizadas até em cada pt (exclui as autormáticas futuras)
    avaliacoes_pt = db.session.query(planos_trabalhos_consolidacoes.plano_trabalho_id,
                                     label('qtd_aval',func.count(avaliacoes.id)))\
                              .join(planos_trabalhos_consolidacoes, planos_trabalhos_consolidacoes.id == avaliacoes.plano_trabalho_consolidacao_id)\
                              .group_by(planos_trabalhos_consolidacoes.plano_trabalho_id)\
                              .subquery()                                            
    
    
    planos_trab_pessoa  = db.session.query(label('pt_id',planos_trabalhos.id.distinct()),
                                           planos_trabalhos.data_inicio,
                                           planos_trabalhos.data_fim,
                                           planos_trabalhos.carga_horaria,
                                           planos_trabalhos.forma_contagem_carga_horaria,
                                           planos_trabalhos.status,
                                           Pessoas.nome,
                                           Unidades.sigla,
                                           label('forma',tipos_modalidades.nome),
                                           avaliacoes_pt.c.qtd_aval)\
                                    .filter(planos_trabalhos.usuario_id == pessoa_id)\
                                    .join(Pessoas, Pessoas.id == planos_trabalhos.usuario_id)\
                                    .outerjoin(planos_trabalhos_entregas, planos_trabalhos_entregas.plano_trabalho_id == planos_trabalhos.id)\
                                    .outerjoin(planos_entregas_entregas, planos_entregas_entregas.id == planos_trabalhos_entregas.plano_entrega_entrega_id)\
                                    .outerjoin(Unidades, Unidades.id == planos_trabalhos.unidade_id)\
                                    .outerjoin(tipos_modalidades, tipos_modalidades.id == planos_trabalhos.tipo_modalidade_id)\
                                    .outerjoin(avaliacoes_pt,avaliacoes_pt.c.plano_trabalho_id == planos_trabalhos.id,)\
                                    .order_by(planos_trabalhos.data_inicio,)\
                                    .all()    

    quantidade = len(planos_trab_pessoa)


    return render_template('consulta_pts_pessoa.html', quantidade = quantidade,
                                                dados_pessoa = dados_pessoa,
                                                planos_trab_pessoa = planos_trab_pessoa)                                                
        

#