from flask import Flask, render_template,request, redirect, url_for, make_response,session
import json
import pdfkit
from  flask  import  Flask 

from caixa import CaixaDiario, depositoPrevio, servicoPrevio
from banco import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

from flask_mysqldb import MySQL
import re 
import MySQLdb.cursors





app = Flask(__name__)
app.secret_key = 'Q1W2E3R4T5Y6'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sistema'
  
mysql = MySQL(app) 






user = None






#lista_deposito_previo = depositoPrevio('4','321.654.963-00','RONEY BARROS FERREIRA- ME','BAIXA/CANCELAMENTO DE CDULA DE CREDITO N° 5043',None,'29/07/2020',None,user)
#lista_deposito_previo1 = depositoPrevio('2','321.654.963-00','MARCELO ALGUNTO CAVOLCANTE','BAIXA/CANCELAMENTO DE CDULA DE CREDITO N° 5043',None,'13/11/2020',None,user)

#all_depositos_previos = [lista_deposito_previo, lista_deposito_previo1]
all_depositos_previos = busca_deposito()

#lista_servico_previo = servicoPrevio('1','102','PROTOCOLO PARA TESTE 1 VIA ','29/07/2020 12:49','10/08/2020 12:49',user,None,False,22.12,lista_deposito_previo.cpf_solicitante,lista_deposito_previo.nome_solicitante,lista_deposito_previo.tipo_documento,lista_deposito_previo.criador,'29/07/2020 12:49')

#lista_servico_previo0 = servicoPrevio('1','100','PROTOCOLO PARA TESTE 2 VIA ','29/07/2020 12:49','10/08/2020 12:49',user,None,False,22.12,lista_deposito_previo.cpf_solicitante,lista_deposito_previo.nome_solicitante,lista_deposito_previo.tipo_documento,lista_deposito_previo.criador,'29/07/2020 12:49')
#lista_servico_previo1 = servicoPrevio('2', '101','PROTOCOLO MARCELO','13/11/2020 12:49','10/08/2020 12:49',user,None,False,19.10,lista_deposito_previo1.cpf_solicitante,lista_deposito_previo1.nome_solicitante,lista_deposito_previo1.tipo_documento,lista_deposito_previo1.criador,'29/07/2020 12:49')
#all_servicos_previos = [lista_servico_previo,lista_servico_previo1,lista_servico_previo0]

serv1 = CaixaDiario(user,'1','19.10','CERTIDAO DE 2° VIA','026.879.987-30','27/10/2020 15:16') 

lista = [serv1]

registro_nome = []
lista_deposito_previo3 =[]



@app.route('/', methods=['GET'])
def login():

    return render_template('login.html')
@app.route('/autenticar', methods=['POST'])
def autenticar ():

    #validar = login_bd(usuario,senha)

    
    if request.method == 'POST' and 'usuario' in request.form and 'senha' in request.form: 
        senha = request.form['senha'] 
        usuario = request.form['usuario']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuario WHERE nome = % s AND senha = % s', (usuario,senha, )) 
        account = cursor.fetchone() 


        
        if account: 
            session['loggedin'] = True
            session['idUsuario'] = account['idUsuario'] 
            session['nome'] = account['nome'] 
            print("******************************")
            print ("SUCESSO NO LOGIN")
            print(session['nome'])
            print("*******************************")
            if session['idUsuario'] == 2:
                
                return redirect('/index_admin') 
            else:
                session.permanent = True
                return redirect('/index_user')
        else: 
            print("ERRO DE LOGIN")
            return redirect('/erro')







    #if validar == True:
    #    if usuario == 'dirce':
    #        return redirect('/index_admin')
    #    else:
    #        return redirect('/index_user')
    #else:
    #    return redirect('/erro') 
    #    ##return redirect('/index')

@app.route('/erro')
def erro():

    return render_template('login_erro.html')
@app.route('/index_user')
def index():
    usuario = session['nome']
    

    return render_template('user/index.html', usuario=usuario)
@app.route('/index_admin')
def index_admin():

    usuario = session['nome']
     
    
    return render_template('admin/index.html', usuario=usuario)



@app.route('/nascimento')
def nascimento():
    usuario = session['nome']
     
    sub_registro = []
    for x in registro_nome:
        sub_registro = x 



    return render_template('livros/nascimento.html',nascimento=sub_registro,usuario=usuario )

@app.route('/busca' ,methods=['GET', 'POST'])
def busca_nascimento():
    registro_nome.clear()
    nome = request.form['nome_sql']
    nome_maiusculo = nome.upper()
    registro_nome.append(busca_nome_bd(nome_maiusculo))
    
    
    return redirect('/nascimento')




@app.route('/casamento')
def casamento():
    with open('static/json/casamentos.json', encoding='utf-8') as f:
        data= json.load(f)
    return render_template('livros/casamento.html',casamentos=data)

@app.route('/obito')
def obito():
    with open('static/json/obitos.json', encoding='utf-8') as f:
        data= json.load(f)
   
    return render_template('livros/obito.html',obitos=data)

@app.route('/tables')
def tables():
    
    

    
    return render_template('tables.html')

@app.route('/servico')
def servico():
    usuario = session['nome']
    
    total = float()
    for i in lista:
       total += float(i.valor) 
                        
  

    return render_template('servico.html',servico =lista, bruto = total,usuario=usuario )
@app.route('/caixadia' ,methods=['GET', 'POST'])
def caixaDoDia():
    from random import randint
    from datetime import datetime
    cpf = request.form['cpf']
    valor = request.form['valor']
    servico = request.form['servico']

    ale =randint(2,100)
    
    data_e_hora_atuais = datetime.now()
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y')
    caixa = CaixaDiario(user,ale,valor,servico,cpf,data_e_hora_em_texto)

    lista.append(caixa)
  
    return redirect('/servico')


@app.route('/previo')
def previo():
    deposito_com_servico_aberto1 =[]
    orcamento = busca_deposito()
    deposito_em_aguardo = []
    todos_depositos = []


    deposito_com_servico_aberto = lista_de_depositos_com_servico_aberto()
    for i in deposito_com_servico_aberto:
        deposito_com_servico_aberto1.append(i[0])
    for i in orcamento:
        if i.pago == 1:
            deposito_em_aguardo = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
            todos_depositos.append(deposito_em_aguardo)
    
            

        
    
    return render_template('admin/cadastro_deposito_previo.html',depositoGlobal= todos_depositos,servico =lista,servico_ativo = deposito_com_servico_aberto1)
@app.route('/previo_pesquisa')
def previo_pesquisa():
    deposito_com_servico_aberto1 =[]
    orcamento = pesquisa_deposito()
    deposito_em_aguardo = []
    todos_depositos = []


    deposito_com_servico_aberto = lista_de_depositos_com_servico_aberto()
    for i in deposito_com_servico_aberto:
        deposito_com_servico_aberto1.append(i[0])
    for i in orcamento:
        if i.pago == 1:
            deposito_em_aguardo = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
            todos_depositos.append(deposito_em_aguardo)
    
            

        
    
    return render_template('admin/pesquisa_deposito.html',depositoGlobal= todos_depositos,servico =lista,servico_ativo = deposito_com_servico_aberto1)

@app.route('/previo_user')
def previo_user():
    deposito_com_servico_aberto1 =[]
    orcamento = busca_global_deposito()
    deposito_em_aguardo = []
    todos_depositos = []


    deposito_com_servico_aberto = lista_de_depositos_com_servico_aberto()
    for i in deposito_com_servico_aberto:
        deposito_com_servico_aberto1.append(i[0])
    for i in orcamento:
        if i.pago == 1:
            deposito_em_aguardo = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
            todos_depositos.append(deposito_em_aguardo)
    
            

        
    
    return render_template('user/deposito_previo_user.html',depositoGlobal= todos_depositos,servico =lista,servico_ativo = deposito_com_servico_aberto1)



@app.route('/apaga_deposito/<cod>' ,methods=['GET', 'POST'])
def apagar_deposito(cod):

    delete_deposito(cod)
    

    #all_depositos_previos.append(busca_deposito(lista_deposito_previo3))
        
    return redirect('/orcamento_user')
@app.route('/apaga_deposito_admin/<cod>' ,methods=['GET', 'POST'])
def apagar_deposito_admin(cod):
    delete_deposito(cod)
    

    #all_depositos_previos.append(busca_deposito(lista_deposito_previo3))
        
    return redirect('/orcamento_admin')
@app.route('/apaga_servico/<ist>/<cod>' ,methods=['GET', 'POST'])
def apagar_servico(ist,cod):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM deposito_previo WHERE iddeposito_previo  = % s', (ist, )) 
    account2 = cursor.fetchone() 
    if account2['pago'] == 1:
        return redirect('/')
    else:

        delete_servico(cod)

   
    return redirect (url_for('orcamento_previo',cod=ist))

@app.route('/apaga_servico_admin/<ist>/<cod>' ,methods=['GET', 'POST'])
def apagar_servico_admin(ist,cod):
    delete_servico(cod)

   
    return redirect (url_for('registro_admin',cod=ist))


@app.route('/recarrega_deposito')
def recarregar_deposito():
    redirect('/previo')


@app.route('/depositoPrevio', methods=['GET','POST'])
def deposito_previo():
    from datetime import datetime
    from random import randint
    cpf = request.form['cpf']
    nome_minusculo = request.form['nome_solicitante']
    nome = nome_minusculo.upper()
    tipo_documento_minus = request.form['tipo_documento']
    tipo_documento = tipo_documento_minus.upper()
    # criador = request.form['criador']
    criador = session['nome']
    id_user = session['idUsuario']

    telefone = request.form['telefone_solicitante']
    #criador = user trazaz a variavel global de log 
    pago = 0
    #print("*********************************")
    #print(criador) 
    #ale =randint(2,100)
    ale2 =randint(100,200)

    data_e_hora_atuais = datetime.now()
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%y/%m/%d')
    if criador == None :
        return redirect('/')

    cadastra_deposito(cpf,nome,tipo_documento,criador,data_e_hora_em_texto,telefone,id_user,pago)

    return redirect('/orcamento_user')

@app.route('/depositoPrevio_admin', methods=['GET','POST'])
def deposito_previo_admin():
    from datetime import datetime
    from random import randint

    cpf = request.form['cpf']
    nome_minusculo = request.form['nome_solicitante']
    nome = nome_minusculo.upper()
    tipo_documento_minus = request.form['tipo_documento']
    tipo_documento = tipo_documento_minus.upper()
    #criador = request.form['criador']
    criador = None
    criador = session['nome']
    telefone = request.form['telefone_solicitante']
    id_user = session['idUsuario']
    pago = 0

    #ale =randint(2,100)
    ale2 =randint(100,200)
    
    data_e_hora_atuais = datetime.now()
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%y/%m/%d')
    if criador == None :
        return redirect('/')

    
    print(criador)
    print('*********************',id_user)
    cadastra_deposito(cpf,nome,tipo_documento,criador,data_e_hora_em_texto,telefone,id_user,pago)

    return redirect('/orcamento_admin')

@app.route('/registro_user/<cod>', methods=['GET','POST'])
def registro(cod):
    total = 0
    servico_realizado = 0
    servico_aberto = 0
    usuario = session['nome']
    
    codigo = int(cod)
    lista_servicos =[]
    lista_doida = []
    
    all_depositos_previos = busca_deposito()
    all_servicos_previos = busca_servico(codigo)


    for i in all_depositos_previos:
        if i.cod_deposito == codigo:
            deposito_serv = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
            lista_doida.append(deposito_serv)
   
    for j in all_servicos_previos:
        if j.cod_deposito == codigo:
            servicos = servicoPrevio(j.cod_deposito,j.cod_servico,j.descricao_servico,j.data_registro,j.data_entrega,j.user_inicio,j.user_fim,j.realizacao,j.valor,j.pago)

            lista_servicos.append(servicos)

            if j.realizacao == 0:
                
                servico_aberto = j.valor + servico_aberto
            if j.realizacao == 1:
                servico_realizado = j.valor + servico_realizado
    total = servico_realizado+servico_aberto

  
    #valor_servico1 = request.form['valor_servico'] 
   
    return render_template('user/lista_previa_servico.html',teste=cod, deposito = lista_doida, servicos = lista_servicos,total=total,servico_aberto=servico_aberto,servico_realizado=servico_realizado,usuario=usuario)

@app.route('/servico_admin/<cod>', methods=['GET','POST'])
def servico_admin(cod):
    total = 0
    servico_realizado = 0
    servico_aberto = 0
    
    codigo = int(cod)
    lista_servicos =[]
    lista_doida = []
    
    all_depositos_previos = busca_deposito()
    all_servicos_previos = busca_servico(codigo)


    for i in all_depositos_previos:
        if i.cod_deposito == codigo:
            deposito_serv = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
            lista_doida.append(deposito_serv)
   
    for j in all_servicos_previos:
        if j.cod_deposito == codigo:
            servicos = servicoPrevio(j.cod_deposito,j.cod_servico,j.descricao_servico,j.data_registro,j.data_entrega,j.user_inicio,j.user_fim,j.realizacao,j.valor,j.pago)

            lista_servicos.append(servicos)

            if j.realizacao == 0:
                
                servico_aberto = j.valor + servico_aberto
            if j.realizacao == 1:
                servico_realizado = j.valor + servico_realizado
    total = servico_realizado+servico_aberto

  
    #valor_servico1 = request.form['valor_servico'] 
   
    return render_template('admin/registro_servico.html',teste=cod, deposito = lista_doida, servicos = lista_servicos,total=total,servico_aberto=servico_aberto,servico_realizado=servico_realizado)


@app.route('/servicoPrevio/<cod>', methods=['GET','POST'])
def servico_previ0(cod): 
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM deposito_previo WHERE iddeposito_previo  = % s', (cod, )) 
    account1 = cursor.fetchone() 
    livre = None

    if account1['pago'] == 1:
        return redirect('/')
    else: 

        from datetime import datetime
        from random import randint
        all_depositos_previos = busca_deposito()
    
        data_e_hora_atuais = datetime.now()
        ale2 =randint(100,200)
        lista_servico=None
        data_e_hora_em_texto = data_e_hora_atuais.strftime('%y/%m/%d')
        codigo = int(cod)
        all_servicos_previos = busca_servico(codigo)
        data_entrega = None
        user_fim = None
        realizado = 0
        servico_previo = request.form['servico_previo']
        valor_servico = request.form['valor_servico']
        servico_previo_maiunsculo = servico_previo.upper()
        pago =0
        criador = session['nome']
        for i in all_depositos_previos:   
            if i.cod_deposito == codigo:

               cadastro_servico(servico_previo_maiunsculo,data_e_hora_em_texto,data_entrega,criador,user_fim,realizado,valor_servico,codigo,pago)
                
                       #cadastro_servico(servico_previo_maiunsculo,data_e_hora_em_texto,data_entrega,j.criador,user_fim,realizado,valor_servico,i.cod_deposito)
    
        return redirect (url_for('orcamento_previo',cod=cod))



@app.route('/comprovante/<cod>', methods=['GET','POST'])
def comprovante(cod):
    codigo = int(cod)
    from reportlab.lib import utils
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from datetime import datetime
    data_e_hora_atuais = datetime.now()
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y')
    total = 0
    servico_realizado = 0
    servico_aberto = 0
    quantidade_geral = 0
    lista_servicos =[]
  

    nome = 'LUCAS CRISTHIAN'
    nome_geral="LUCAS CRISTHIAN SILVEIRA DE OLIVEIRA"
    
    
    lista_doida = []


    
    
    all_depositos_previos = busca_deposito()
    all_servicos_previos = busca_servico(cod)

  
    for i in all_depositos_previos:
        deposito_serv = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
        lista_doida.append(deposito_serv)

    for x in lista_doida:
        if x.cod_deposito == codigo:
            nome = x.nome_solicitante
            natureza = x.tipo_documento
            cpf = x.cpf_solicitante
            telefone = x.telefone
            data_orcamento = x.data_criacao
            

            nome_geral = buscar_usuario(x.criador)

            
   
    for j in all_servicos_previos:

            servicos = servicoPrevio(j.cod_deposito,j.cod_servico,j.descricao_servico,j.data_registro,j.data_entrega,j.user_inicio,j.user_fim,j.realizacao,j.valor,j.pago)

            lista_servicos.append(servicos)

            if j.realizacao == 0:
                
                servico_aberto = j.valor + servico_aberto
            if j.realizacao == 1:
                servico_realizado = j.valor + servico_realizado




    total = str(servico_realizado+servico_aberto)


    

  
    output = BytesIO()  
    p = canvas.Canvas(output)
    p.setTitle('Orçamento')

    image_path ="../Deposito_previo_2.0-oficial/static/img/cart.jpg"
    img = utils.ImageReader(image_path)
    img_width, img_height = img.getSize()
    aspect = img_height / float(img_width)
 
    p.saveState()

   
  

    

    
    p.drawImage(image_path, 225, 765,
               width=200, height=(150 * aspect))
    p.restoreState()
    
    
    p.drawString(105,750,'SERVENTIA EXTRAJUDICIAL DA COMARCA DE SENA MADUREIRA/AC')
    p.line(30,735,580,735)
    p.drawString(275,720,'ORÇAMENTO')
    p.setFont('Times-Roman',9)
    
    p.drawString(33,703,'SOLICITANTE:')
    p.line(30,700,580,700)
    p.drawString(120,703,nome)
    
    
    p.drawString(33,685,'NATUREZA:')
    p.line(30,682,580,682)
    p.drawString(103,685,natureza)

    p.drawString(31,667,'CPF/CNPJ:')
    p.line(30,664,580,664)
    p.line(152,682,152,664)

    p.drawString(75,667,cpf)
    p.drawString(154,667,'TELEFONE:')
    p.drawString(225,667,telefone)

    p.line(315,682,315,664)
    p.drawString(318,667,'SERVIÇO:')
    p.drawString(400,667,cod)

    p.line(427,682,427,664)
    p.drawString(429,667,'DATA:')
    date = data_orcamento.strftime("%d/%m/%Y")
    p.drawString(470,667,date)


    p.drawString(33,651,'DADOS BANCARIOS : (SICOOB nº 756 Agencia:5038 - CONTA: 109.683-4) - Serventia Extrajudicial da Comarca de Sena Madureira ')
    p.drawString(35,637,'PIX : cartoriosena@gmail.com')
    




    
    p.drawString(215,618,'DESCRIÇÃO DOS SERVIÇOS')
    p.drawString(525,618,'VALOR')
    p.line(30,634,580,634)

    

    
    for l in lista_servicos:
        quantidade_geral += 1



   # quantidade de linhas para serviços
    linha = 616 
    
    for r in range(quantidade_geral):
        
        p.line(30,linha,580,linha)
        linha = (linha-18)
        p.line(30,linha,580,linha)
    linha -=18
    p.line(30,linha,580,linha) # preenchimento da linha do valor total    
    p.line(30,735,30,linha) # linha esquerda    
    p.line(500,634,500,linha) # linha esquerda valores
    p.line(580,735,580,linha) # linha direita
    p.line(30,718,580,718)
    

    # serviços 
    local_linha = 601
    for m in lista_servicos:
        valor_serv = str(m.valor)
        p.drawString(40,local_linha,m.descricao_servico)
        p.drawString(515,local_linha,'R$  '+valor_serv)
        local_linha -= 18
        
  

    p.drawString(521,local_linha,'R$ '+total)
    p.drawString(521,local_linha,'R$ '+total)
   
    p.drawString(250,local_linha,'VALOR TOTAL')
    p.drawString(250,local_linha,'VALOR TOTAL')
    local_observa = local_linha - 16



    local_linha -= 64
    p.line(100,local_linha,510,local_linha)
    local_linha -= 20
    p.drawString(188,local_linha,nome_geral)
    local_linha -=15
    p.drawString(175,local_linha,'Sena Madureira / Acre - Data De Impressão ( {} )'.format(data_e_hora_em_texto))
    
    p.drawString(33,local_observa,'Observação:')
    local_observa = local_observa - 14
    p.drawString(33,local_observa,'*Valores sujeiros a alteração. Caso não seja possível efetuar o serviço, serão devolvidos os emolumentos cobrados com a dedução das buscas e da')
    local_observa = local_observa - 14
    p.drawString(33,local_observa,'prenotação nos termos do art. 206, da lei 6.015/73')
    p.showPage()
    p.save()

    pdf_out = output.getvalue()
    output.close()  
    response = make_response(pdf_out)
    response.headers['Content-Disposition'] ="attachment; filename=Orçamento-({}-{}).pdf".format(nome,natureza)
    response.mimetype = 'application/pdf'




    return response
@app.route('/recibo/<cod>', methods=['GET','POST'])
def recibo(cod):
    codigo = int(cod)
    from reportlab.lib import utils
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from datetime import datetime
    data_e_hora_atuais = datetime.now()
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y')
    total = 0
    servico_realizado = 0
    servico_aberto = 0
    quantidade_geral = 0
    lista_servicos =[]
  

    nome = 'LUCAS CRISTHIAN'
    nome_geral="LUCAS CRISTHIAN SILVEIRA DE OLIVEIRA"
    
    
    lista_doida = []
    
    all_depositos_previos = busca_deposito()
    all_servicos_previos = busca_servico(cod)

  
    for i in all_depositos_previos:
        deposito_serv = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
        lista_doida.append(deposito_serv)

    for x in lista_doida:
        if x.cod_deposito == codigo:
            nome = x.nome_solicitante
            natureza = x.tipo_documento
            cpf = x.cpf_solicitante
            telefone = x.telefone
            data_orcamento = x.data_criacao
            

            nome_geral = buscar_usuario(x.criador)

        	
   
    for j in all_servicos_previos:

            servicos = servicoPrevio(j.cod_deposito,j.cod_servico,j.descricao_servico,j.data_registro,j.data_entrega,j.user_inicio,j.user_fim,j.realizacao,j.valor,j.pago)

            lista_servicos.append(servicos)

            if j.realizacao == 0:
                
                servico_aberto = j.valor + servico_aberto
            if j.realizacao == 1:
                servico_realizado = j.valor + servico_realizado




    total = str(servico_realizado+servico_aberto)


    

  
    output = BytesIO()  
    p = canvas.Canvas(output)
    p.setTitle('Recibo')

    image_path ="../Deposito_previo_2.0-oficial/static/img/cart.jpg"
    img = utils.ImageReader(image_path)
    img_width, img_height = img.getSize()
    aspect = img_height / float(img_width)
 
    p.saveState()

   
  

    

    
    p.drawImage(image_path, 225, 765,
               width=200, height=(150 * aspect))
    p.restoreState()
    
    
    p.drawString(105,750,'SERVENTIA EXTRAJUDICIAL DA COMARCA DE SENA MADUREIRA/AC')
    p.line(30,735,580,735)
    p.drawString(275,720,'RECIBO')
    p.setFont('Times-Roman',9)
    
    p.drawString(33,703,'SOLICITANTE:')
    p.line(30,700,580,700)
    p.drawString(120,703,nome)
    
    
    p.drawString(33,685,'NATUREZA:')
    p.line(30,682,580,682)
    p.drawString(103,685,natureza)

    p.drawString(33,667,'CPF/CNPJ:')
    p.line(30,664,580,664)
    p.line(152,682,152,664)

    p.drawString(75,667,cpf)
    p.drawString(154,667,'TELEFONE:')
    p.drawString(225,667,telefone)

    p.line(315,682,315,664)
    p.drawString(318,667,'SERVIÇO:')
    p.drawString(400,667,cod)

    p.line(427,682,427,664)
    p.drawString(429,667,'DATA:')
    date = data_orcamento.strftime("%d/%m/%Y")
    p.drawString(470,667,date)
  



    
    p.drawString(215,618,'DESCRIÇÃO DOS SERVIÇOS')
    p.drawString(525,618,'VALOR')
    p.line(30,634,580,634)

    

    
    for l in lista_servicos:
        quantidade_geral += 1



   # quantidade de linhas para serviços
    linha = 616 
    
    for r in range(quantidade_geral):
        
        p.line(30,linha,580,linha)
        linha = (linha-18)
        p.line(30,linha,580,linha)
    linha -=18
    p.line(30,linha,580,linha) # preenchimento da linha do valor total    
    p.line(30,735,30,linha) # linha esquerda    
    p.line(500,634,500,linha) # linha esquerda valores
    p.line(580,735,580,linha) # linha direita
    p.line(30,718,580,718)
    

    # serviços 
    local_linha = 601
    for m in lista_servicos:
        valor_serv = str(m.valor)
        p.drawString(40,local_linha,m.descricao_servico)
        p.drawString(515,local_linha,'R$  '+valor_serv)
        local_linha -= 18
        
  

    p.drawString(521,local_linha,'R$ '+total)
    p.drawString(521,local_linha,'R$ '+total)
   
    p.drawString(250,local_linha,'VALOR TOTAL')
    p.drawString(250,local_linha,'VALOR TOTAL')

    local_linha -= 64
    p.line(100,local_linha,510,local_linha)
    local_linha -= 20
    #p.drawString(188,local_linha,nome_geral)
    local_linha -=15
    p.drawString(175,local_linha,'Sena Madureira / Acre - Data De Impressão ( {} )'.format(data_e_hora_em_texto))
    
    p.showPage()
    p.save()

    pdf_out = output.getvalue()
    output.close()  
    response = make_response(pdf_out)
    response.headers['Content-Disposition'] ="attachment; filename=Recibo- {} .pdf".format(nome)
    response.mimetype = 'application/pdf'




    return response


@app.route('/atualiza/<ist>/<cod>', methods=['GET','POST'])
def atualiza_servico(ist,cod):
    from datetime import datetime
    usuario = session['nome']
    data_e_hora_atuais = datetime.now()
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%y/%m/%d')
    if usuario == None:
        return redirect('/')

    atualizar_servico(cod,data_e_hora_em_texto,usuario)



    return redirect (url_for('registro',cod=ist))




@app.route('/orcamento_user')
def orcamento():
    usuario = session['nome']
    usuario=usuario
    all_depositos_previos = busca_deposito()
    deposito_com_servico_nao_pagos = []
    deposito_pago =[]
    for i in all_depositos_previos:
        if i.pago == 0:
            deposito_pago = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
            deposito_com_servico_nao_pagos.append(deposito_pago)
   
        
    
    return render_template('user/orcamento_user.html',depositoGlobal= deposito_com_servico_nao_pagos,servico =lista,usuario=usuario)





@app.route('/servicoPrevio_admin/<cod>', methods=['GET','POST'])
def servico_previ0_admin(cod):  
    from datetime import datetime
    from random import randint
    all_depositos_previos = busca_deposito()
   
    data_e_hora_atuais = datetime.now()
    ale2 =randint(100,200)
    lista_servico=None
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%y/%m/%d')
    codigo = int(cod)
    all_servicos_previos = busca_servico(codigo)
    data_entrega = None
    user_fim = None
    realizado = 0
    servico_previo = request.form['servico_previo']
    valor_servico = request.form['valor_servico']
    servico_previo_maiunsculo = servico_previo.upper()
    pago =0
    for i in all_depositos_previos:   
        if i.cod_deposito == codigo:
            cadastro_servico(servico_previo_maiunsculo,data_e_hora_em_texto,data_entrega,i.criador,user_fim,realizado,valor_servico,codigo,pago)
             
                #cadastro_servico(servico_previo_maiunsculo,data_e_hora_em_texto,data_entrega,j.criador,user_fim,realizado,valor_servico,i.cod_deposito)

    return redirect (url_for('registro_admin',cod=cod))





@app.route('/atualiza_admin/<ist>/<cod>', methods=['GET','POST'])
def atualiza_servico_admin(ist,cod):
    from datetime import datetime
    data_e_hora_atuais = datetime.now()
    data_e_hora_em_texto = data_e_hora_atuais.strftime('%y/%m/%d')
    usuario = session['nome']
    if usuario == None:
        return redirect ('/')
    atualizar_servico(cod,data_e_hora_em_texto,usuario)



    return redirect (url_for('registro_admin_servico',cod=ist))



@app.route('/depositoPrevioTotal_admin')
def DepositoPrevio():
    from datetime import datetime
    
    total = 0.0
    
    data_e_hora_atuais = datetime.now()
    data = data_e_hora_atuais.strftime('%y/%m/%d')
    servico_do_dia =[]
    pendente = servicos_abertos()
  
    qtd = qtd_servicos_abertos()

    servicos_dia = servicos_realizado_dia(data)
    for i in servicos_dia:
        servico_do_dia.append(i)
    for i in servico_do_dia:

        parte = i[3]

        parte1 = float(parte)
       

       
        total = total + parte1
      
       
    
    return render_template('admin/deposito_previo.html',pendente=pendente,caixa=32000,qtd_servicos = qtd,servico_do_dia=servico_do_dia,total = total)


@app.route('/orcamento_previo/<cod>',methods=['GET','POST'])
def orcamento_previo(cod):
    total = 0
    servico_realizado = 0
    servico_aberto = 0
    usuario = session['nome']
    if usuario == None:
        return redirect ('/')
    codigo = int(cod)
    lista_servicos =[]
    lista_doida = []
    
    all_depositos_previos = busca_deposito()
    all_servicos_previos = busca_servico(codigo)


    for i in all_depositos_previos:
        if i.cod_deposito == codigo:
            deposito_serv = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
            lista_doida.append(deposito_serv)
   
    for j in all_servicos_previos:
        if j.cod_deposito == codigo:
            servicos = servicoPrevio(j.cod_deposito,j.cod_servico,j.descricao_servico,j.data_registro,j.data_entrega,j.user_inicio,j.user_fim,j.realizacao,j.valor,j.pago)

            lista_servicos.append(servicos)

            if j.realizacao == 0:
                
                servico_aberto = j.valor + servico_aberto
            if j.realizacao == 1:
                servico_realizado = j.valor + servico_realizado
    total = servico_realizado+servico_aberto

  
    #valor_servico1 = request.form['valor_servico'] 
   
    return render_template('user/orcamento_previo_user.html',teste=cod, deposito = lista_doida, servicos = lista_servicos,total=total,servico_aberto=servico_aberto,servico_realizado=servico_realizado,usuario = usuario)


@app.route('/registro_admin/<cod>', methods=['GET','POST'])
def registro_admin(cod):
    if session['idUsuario'] != 2 : 
        return redirect('/')
    all_depositos_previos = busca_deposito()
    total = 0
    servico_realizado = 0
    servico_aberto = 0
    usuario = session['nome']
    if usuario == None:
        return redirect ('/')
    codigo = int(cod)
    lista_servicos =[]
    lista_doida = []
    
    all_depositos_previos = busca_deposito()
    all_servicos_previos = busca_servico(codigo)


    for i in all_depositos_previos:
        if i.cod_deposito == codigo:
            deposito_serv = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
            lista_doida.append(deposito_serv)
   
    for j in all_servicos_previos:
        if j.cod_deposito == codigo:
            servicos = servicoPrevio(j.cod_deposito,j.cod_servico,j.descricao_servico,j.data_registro,j.data_entrega,j.user_inicio,j.user_fim,j.realizacao,j.valor,j.pago)

            lista_servicos.append(servicos)

            if j.realizacao == 0:
                
                servico_aberto = j.valor + servico_aberto
            if j.realizacao == 1:
                servico_realizado = j.valor + servico_realizado
    total = servico_realizado+servico_aberto

  
    #valor_servico1 = request.form['valor_servico'] 
   
    return render_template('admin/orcamento_previo_admin.html',teste=cod, deposito = lista_doida, servicos = lista_servicos,total=total,servico_aberto=servico_aberto,servico_realizado=servico_realizado, usuario = usuario)

@app.route('/registro_admin_servico/<cod>', methods=['GET','POST'])
def registro_admin_servico(cod):
    if session['idUsuario'] != 2 : 
        return redirect('/')
    all_depositos_previos = busca_deposito()
    total = 0
    servico_realizado = 0
    servico_aberto = 0
    usuario = session['nome']
    if usuario == None:
        return redirect ('/')
    codigo = int(cod)
    lista_servicos =[]
    lista_doida = []
    
    all_depositos_previos = busca_deposito()
    all_servicos_previos = busca_servico(codigo)


    for i in all_depositos_previos:
        if i.cod_deposito == codigo:
            deposito_serv = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
            lista_doida.append(deposito_serv)
   
    for j in all_servicos_previos:
        if j.cod_deposito == codigo:
            servicos = servicoPrevio(j.cod_deposito,j.cod_servico,j.descricao_servico,j.data_registro,j.data_entrega,j.user_inicio,j.user_fim,j.realizacao,j.valor,j.pago)

            lista_servicos.append(servicos)

            if j.realizacao == 0:
                
                servico_aberto = j.valor + servico_aberto
            if j.realizacao == 1:
                servico_realizado = j.valor + servico_realizado
    total = servico_realizado+servico_aberto

  
    #valor_servico1 = request.form['valor_servico'] 
   
    return render_template('admin/registro_servico.html',teste=cod, deposito = lista_doida, servicos = lista_servicos,total=total,servico_aberto=servico_aberto,servico_realizado=servico_realizado, usuario = usuario)



@app.route('/orcamento_admin')
def orcamento_admin():
    if session['idUsuario'] != 2 : 
        return redirect('/')

    all_depositos_previos = busca_deposito()
    deposito_com_servico_nao_pagos = []
    deposito_pago =[]
    usuario = session['nome']
    for i in all_depositos_previos:
        if i.pago == 0:
            deposito_pago = depositoPrevio(i.cod_deposito,i.cpf_solicitante,i.nome_solicitante,i.tipo_documento,i.criador,i.data_criacao,i.telefone,i.usuario,i.pago)
            deposito_com_servico_nao_pagos.append(deposito_pago)
            
        
    
    return render_template('admin/orcamento_admin.html',depositoGlobal= deposito_com_servico_nao_pagos,servico =lista, usuario= usuario)
    
    
@app.route('/versenha/<numero>', methods=['GET','POST'])
def versenha(numero):
    
  
    
    return render_template('atendimento/visualizarsenha.html',numero=numero)
@app.route('/gerarsenha')
def gerarsenha():
    from random import randint
    numero =randint(10,20)
    return redirect (url_for('versenha',numero=numero))
 
@app.route('/pagamento/<cod>',methods=['GET','POST'])
def pagamento(cod):
    print('PAGAMENTO EM ANDAMENTO',cod)
    pagamento_servico(cod)
    return redirect (url_for('servico_admin',cod=cod))

@app.route('/servicoDiario_user')
def servico_diario_user():

    return render_template('user/servico_diario.html')

@app.route('/perfil_de_usuario')
def perfil_de_usuario():
    cod = session['idUsuario']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM usuario WHERE idUsuario  = % s', (cod, )) 
    account3 = cursor.fetchone() 
    
    id_nome = account3['idUsuario']
    nome_acesso = account3['nome']
    nome_completo =account3['nome_completo']
    return render_template('user/perfil_user.html',id_nome=id_nome,nome_acesso=nome_acesso,nome_completo=nome_completo)

@app.route('/atualiza_usuario',methods=['GET','POST'])
def atualiza_usuario():
    cod = session['idUsuario']
    senha_acesso = request.form['senha_de_acesso'] 
    #acesso = request.form['nome_acesso']
    #nome = request.form['nome_completo']
    

    sql = "UPDATE usuario SET senha = %s WHERE idUsuario = %s";
    val = (senha_acesso,cod)
    mycursor.execute(sql,val)

    
 



    return redirect('/')




if __name__ == '__main__':
   app.run(host= '0.0.0.0',debug=True,port='5000')