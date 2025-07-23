"""
.. topic:: Unidades (views)

    As Unidades na estrutura da instituição.

.. topic:: Ações relacionadas às Unidades

    * lista_unidades: Lista Unidades
    * lista_unidades_filtro: Lista Unidades conforme filtro aplicado

"""

# views.py na pasta unidades

from flask import render_template,request,Blueprint
from flask_login import current_user, login_required

from sqlalchemy import func, distinct
from sqlalchemy.sql import label
from project import db
from project.models import Unidades, Pessoas, unidades_integrantes, unidades_integrantes_atribuicoes, cidades
from project.unidades.forms import PesquisaUnidForm


unidades = Blueprint('unidades',__name__, template_folder='templates')


## lista unidades da instituição

@unidades.route('/lista_unidades')

def lista_unidades():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das unidades da instituição.                                       |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """ 
    
    lista = '%'
    # Preparação para leitura de unidades

    qtd_unids = db.session.query(Unidades).count()

    page = request.args.get('page', 1, type=int)

    # unids_pai = db.session.query(Unidades.id,
    #                              Unidades.sigla)\
    #                       .filter(Unidades.deleted_at == None)\
    #                       .subquery()

    # subqueries para ver quantos gestores cada unidade tem
    
    chefes_s = db.session.query(Pessoas.id,
                              Pessoas.nome,
                              unidades_integrantes.unidade_id,
                              unidades_integrantes_atribuicoes.atribuicao)\
                       .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                       .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                       .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                               unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                       .subquery()
    substitutos_s = db.session.query(Pessoas.id,
                                   Pessoas.nome,
                                   unidades_integrantes.unidade_id,
                                   unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                            .subquery()
    delegados_s = db.session.query(Pessoas.id,
                                   Pessoas.nome,
                                   unidades_integrantes.unidade_id,
                                   unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_DELEGADO')\
                            .subquery()
                          
    # consultas que repetem as subqueries para poder listar os nomes em um modal
    
    chefes = db.session.query(Pessoas.id,
                              Pessoas.nome,
                              unidades_integrantes.unidade_id,
                              unidades_integrantes_atribuicoes.atribuicao)\
                       .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                       .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                       .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                               unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                       .all()
    substitutos = db.session.query(Pessoas.id,
                                   Pessoas.nome,
                                   unidades_integrantes.unidade_id,
                                   unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                            .all()
    delegados = db.session.query(Pessoas.id,
                                 Pessoas.nome,
                                 unidades_integrantes.unidade_id,
                                 unidades_integrantes_atribuicoes.atribuicao)\
                          .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                          .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                          .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                  unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_DELEGADO')\
                          .all()                      
    
    # sobre paginação    
    pag = 500

    unids = db.session.query(Unidades.id,
                             Unidades.sigla,
                             Unidades.nome,
                             Unidades.unidade_pai_id,
                             cidades.uf,
                             Unidades.path,
                             Unidades.codigo,
                             label('titular',chefes_s.c.nome),
                             label('substituto',func.count(distinct(substitutos_s.c.nome))),
                             label('delegado',func.count(distinct(delegados_s.c.nome))))\
                        .outerjoin(cidades, cidades.id == Unidades.cidade_id)\
                        .outerjoin(chefes_s, chefes_s.c.unidade_id == Unidades.id)\
                        .outerjoin(substitutos_s, substitutos_s.c.unidade_id == Unidades.id)\
                        .outerjoin(delegados_s, delegados_s.c.unidade_id == Unidades.id)\
                        .filter(Unidades.deleted_at == None)\
                        .order_by(Unidades.sigla)\
                        .group_by(Unidades.id,chefes_s.c.nome)\
                        .paginate(page=page,per_page=pag)

    quantidade = unids.total 
    
    caminho = db.session.query(Unidades.path,Unidades.sigla,Unidades.id).all()
    caminho_dict = {}
    for c in caminho:
        if c.path != None and c.path != '':
            p = c.path.split('/')
            arvore = ''
            for i in p:
                if len(i) > 0:
                    sigla_arvore = db.session.query(Unidades.sigla).filter(Unidades.id == i).first()
                    if sigla_arvore != None:
                        arvore += sigla_arvore.sigla+'/'
            arvore += c.sigla
            caminho_dict[c.id] = arvore 
        else:
            caminho_dict[c.id] = c.sigla              
 

    return render_template('lista_unidades.html', unids = unids, quantidade = quantidade, chefes = chefes,
                                                  substitutos = substitutos, delegados = delegados,
                                                  caminho_dict = caminho_dict, lista = lista, qtd_unids=qtd_unids)

    

## lista unidades da instituição

@unidades.route('<lista>/lista_unidades_filtro', methods=['GET','POST'])

def lista_unidades_filtro(lista):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das unidades da instituição de acordo com filtro aplicado.         |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """ 

    page = request.args.get('page', 1, type=int)

    
    
    form = PesquisaUnidForm()
    
    unids = db.session.query(Unidades.sigla)\
                      .filter(Unidades.deleted_at == None)\
                      .order_by(Unidades.sigla).all()
    lista_unids = [(u.sigla,u.sigla) for u in unids]
    lista_unids.insert(0,('','Todas'))  
    
    unids_pai = db.session.query(Unidades.id,
                                 Unidades.sigla)\
                          .filter(Unidades.deleted_at == None)\
                          .order_by(Unidades.sigla).all()
    lista_pais = [(u.id,u.sigla) for u in unids_pai]
    lista_pais.insert(0,('','Todas'))                                


    form.sigla.choices = lista_unids
    form.pai.choices   = lista_pais


    if form.validate_on_submit():

        if form.sigla.data == '':
            p_sigla_pattern = '%'
        else:
            p_sigla_pattern = '%'+form.sigla.data+'%'
            
        if form.pai.data == '':
            p_pai_pattern = '%'
        else:
            p_pai_pattern = '%'+form.pai.data+'%'

        # pega valores utilizados como filtro para exibição na tela da lista
        p_sigla = dict(form.sigla.choices).get(form.sigla.data)
        p_pai   = dict(form.pai.choices).get(form.pai.data)
    
        # Lê tabela unidades

        chefes_s = db.session.query(Pessoas.id,
                                    Pessoas.nome,
                                    unidades_integrantes.unidade_id,
                                    unidades_integrantes_atribuicoes.atribuicao)\
                        .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                        .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                        .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                        .subquery()
        substitutos_s = db.session.query(Pessoas.id,
                                    Pessoas.nome,
                                    unidades_integrantes.unidade_id,
                                    unidades_integrantes_atribuicoes.atribuicao)\
                                .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                        unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                                .subquery()
        delegados_s = db.session.query(Pessoas.id,
                                    Pessoas.nome,
                                    unidades_integrantes.unidade_id,
                                    unidades_integrantes_atribuicoes.atribuicao)\
                                .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                        unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_DELEGADO')\
                                .subquery()
                            
        # consultas que repetem as subqueries para poder listar os nomes em um modal
        
        chefes = db.session.query(Pessoas.id,
                                  Pessoas.nome,
                                  unidades_integrantes.unidade_id,
                                  unidades_integrantes_atribuicoes.atribuicao)\
                        .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                        .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                        .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                        .all()
        substitutos = db.session.query(Pessoas.id,
                                    Pessoas.nome,
                                    unidades_integrantes.unidade_id,
                                    unidades_integrantes_atribuicoes.atribuicao)\
                                .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                        unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                                .all()
        delegados = db.session.query(Pessoas.id,
                                    Pessoas.nome,
                                    unidades_integrantes.unidade_id,
                                    unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_DELEGADO')\
                            .all()

        unids = db.session.query(Unidades.id,
                                 Unidades.sigla,
                                 Unidades.nome,
                                 Unidades.unidade_pai_id,
                                 cidades.uf,
                                 Unidades.path,
                                 Unidades.codigo,
                                 label('titular',chefes_s.c.nome),
                                 label('substituto',func.count(distinct(substitutos_s.c.nome))),\
                                 label('delegado',func.count(distinct(delegados_s.c.nome))))\
                           .outerjoin(cidades, cidades.id == Unidades.cidade_id)\
                           .outerjoin(chefes_s, chefes_s.c.unidade_id == Unidades.id)\
                           .outerjoin(substitutos_s, substitutos_s.c.unidade_id == Unidades.id)\
                           .outerjoin(delegados_s, delegados_s.c.unidade_id == Unidades.id)\
                           .filter(Unidades.sigla.like(p_sigla_pattern),
                                   Unidades.unidade_pai_id.like(p_pai_pattern),
                                   Unidades.nome.like('%'+form.nome.data+'%'),
                                   cidades.uf.like('%'+form.uf.data+'%'))\
                           .order_by(Unidades.sigla)\
                           .group_by(Unidades.id,chefes_s.c.nome)\
                           .paginate(page=page,per_page=500)

        quantidade = unids.total
        
        caminho = db.session.query(Unidades.path,Unidades.sigla,Unidades.id).all()
        caminho_dict = {}
        for c in caminho:
            if c.path != None and c.path != '':
                p = c.path.split('/')
                arvore = ''
                for i in p:
                    if len(i) > 0:
                        sigla_arvore = db.session.query(Unidades.sigla).filter(Unidades.id == i).first()
                        if sigla_arvore != None:
                             arvore += sigla_arvore.sigla+'/'
                arvore += c.sigla
                caminho_dict[c.id] = arvore 
            else:
                caminho_dict[c.id] = c.sigla

        return render_template('lista_unidades.html', unids = unids, quantidade = quantidade,
                                                      lista = lista,
                                                      p_sigla = p_sigla,
                                                      p_pai = p_pai,
                                                      p_nome = form.nome.data,
                                                      p_uf = form.uf.data,
                                                      chefes = chefes,
                                                      substitutos = substitutos, delegados = delegados,
                                                      caminho_dict = caminho_dict,)

    return render_template('pesquisa_unidades.html', form = form)

#
