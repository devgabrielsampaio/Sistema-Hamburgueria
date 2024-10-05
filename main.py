from flask import Flask,render_template,flash,redirect,request,session
from flask_socketio import emit, SocketIO
from forms import FormLogin, FormCriarConta, FormConsultarProduto, FormRelatorioProdutos, FormCadastrarProduto, \
    FormAtualizarProduto, FormCadastrarFornecedores, FormConsultarFornecedores, FormAtualizarFornecedores, \
    FormFinalizacaoVendas, FormRelatorioUsuarios, FormRelatorioFornecedores
from validate_docbr import CPF
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import date, datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import requests
import procedimentos
import math
from datetime import date
app=Flask(__name__)
socketio = SocketIO(app)
app.config['SECRET_KEY']='ac79d97419d4f98857c5cf7f26f14b97'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='hamburgueria'
mysql=MySQL(app)
global linha
@app.route('/')
def home():
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    return render_template('home.html')

@app.route('/criarconta',methods=['GET','POST'])
def criarconta():
    form_criarconta=FormCriarConta()
    if form_criarconta.validate_on_submit():
        cpf=CPF()
        if cpf.validate(form_criarconta.cpf.data)==True:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            try:
                cursor.execute('insert into entrada (CPF,Nome,Email,Senha,Genero) values ("{}","{}","{}","{}","{}")'.format(request.form['cpf'],request.form['username'],request.form['email'],request.form['senha'],request.form['genero']))
                flash("Conta Criada com Sucesso!", "alert-success")
                return redirect("/login")
            except:
                flash("Erro ao Cadastrar Conta","alert-danger")
            finally:
                mysql.connection.commit()
                cursor.close()
        else:
            flash("CPF Inválido","alert-danger")
    return render_template('criarconta.html',form_criarconta=form_criarconta)

@app.route('/login',methods=['GET','POST'])
def login():
    form_login=FormLogin()
    if form_login.validate_on_submit():
        cpf=request.form['cpf']
        senha=request.form['senha']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'select *from entrada where cpf= "{cpf}" and senha="{senha}"')
        resultado=cursor.fetchone()
        if resultado:
            session['loggedin']=True
            session['id']=resultado['CPF']
            session['username']=resultado['Nome']
            session['email']=resultado['Email']
            session['genero']=resultado['Genero']
            flash("Login Feito com Sucesso!", "alert-success")
            return redirect("/")
        else:
            flash("Login ou Senha Incorretos","alert-danger")
        mysql.connection.commit()
        cursor.close()
    return render_template('login.html',form_login=form_login)
@app.route('/meuperfil')
def meuperfil():
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    try:
        formatopalavra=str(session['id'])[9:11]
        cpf=str(session['id'])[0:3]+".***.***-"+formatopalavra
        cursor = mysql.connection.cursor(MySQLdb.cursors.SSCursor)
        cursor.execute(f'SELECT count(*) as c from vendas where CPF_Entrada="{session['id']}"')
        resultado = cursor.fetchall()
        resultado=resultado[0]
        if resultado:
            dados = {"cpf": cpf, "username": session['username'], "email": session['email'],
                     "genero": session['genero'],"vendas":resultado[0]}
    except:
        flash("Erro ao Passar Informações ao Perfil", "alert-danger")
        return redirect("/login")
    finally:
        mysql.connection.commit()
        cursor.close()
    return render_template('meuperfil.html',dados=dados)
@app.route('/sair')
def sair():
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    session.pop('email',None)
    session.pop('genero', None)
    flash("Logout realizado com Sucesso","alert-success")
    return redirect("/login")
@app.route("/cadastrarproduto",methods=['GET','POST'])
def cadastrarproduto():
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    form_cadastrarproduto=FormCadastrarProduto()
    if form_cadastrarproduto.validate_on_submit():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.SSCursor)
            cursor.execute(f'select *from produto where nome="{request.form['nome']}"')
            resultado=cursor.fetchall()
            if resultado:
                flash("Produto Previamente Cadastrado","alert-danger")
            else:
                cursor.execute('insert into produto (Nome,Descricao,Preco) values ("{}","{}",{})'.format(request.form['nome'],request.form['descricao'],float(request.form['preco'])))
                flash("Produto Cadastrado com Sucesso","alert-success")
        except Exception as e:
            print(str(e))
            flash("Erro ao Cadastrar Produto","alert-danger")
        finally:
            mysql.connection.commit()
            cursor.close()
    return render_template("cadastrarproduto.html",form_cadastrarproduto=form_cadastrarproduto)
@app.route("/consultarproduto",methods=['GET','POST'])
def consultarproduto():
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    form_consultar=FormConsultarProduto()
    try:
        cursor=mysql.connection.cursor(MySQLdb.cursors.SSCursor)
        cursor.execute('select ID,Nome,Descricao,Preco from produto')
        resultado=cursor.fetchall()
    except:
        resultado=["#"]
        flash("Erro no Carregamento","alert-danger")
    finally:
        mysql.connection.commit()
        cursor.close()
    if form_consultar.validate_on_submit():
        nome=request.form['nome']
        try:
            cursor=mysql.connection.cursor(MySQLdb.cursors.SSCursor)
            cursor.execute(f'select ID,Nome,Descricao,Preco from produto where Nome like "{nome}%"')
            resultado=cursor.fetchall()
            if resultado:
                pass
            else:
                flash("Produto Não Cadastrado","alert-danger")
        except:
            resultado = ["#"]
            flash("Erro no Carregamento", "alert-danger")
        finally:
            mysql.connection.commit()
            cursor.close()
    return render_template('consultarproduto.html',resultado=resultado,form_consultar=form_consultar)
@app.route("/relatorioprodutos",methods=['GET','POST'])
def relatorioprodutos():
    form_relatorioProdutos=FormRelatorioProdutos()
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    if form_relatorioProdutos.validate_on_submit():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.SSCursor)
            cursor.execute(f'select ID,Nome,Preco from produto where Nome like "{request.form['nome']}%"')
            resultado = cursor.fetchall()
            if resultado:
                pass
            else:
                flash("Produto Não Cadastrado","alert-danger")
        except:
            resultado = ["#"]
            flash("Erro no Carregamento", "alert-danger")
        finally:
            mysql.connection.commit()
            cursor.close()
        file=f"relatorioproduto-{date.today().strftime('%d-%m-%Y')}.pdf"
        cnv = canvas.Canvas("C:\\Users\\aluno\\Downloads\\"+file, pagesize=letter)
        cnv.setFillColorRGB(1, 0, 0)
        cnv.setFont("Helvetica", 40)
        cnv.setFillColorRGB(0, 0, 0)
        cnv.setFont("Times-Roman", 22)
        cnv.drawRightString(1.3 * inch, 8.3 * inch, 'ID:')
        cnv.drawRightString(3.5 * inch, 8.3 * inch, 'Nome:')
        cnv.drawRightString(6.5 * inch, 8.3 * inch, 'Preço')
        cnv.setStrokeColorCMYK(0,0,0,1)
        cnv.line(2* inch, 8.5 * inch, 2 * inch, 2.7 * inch)
        cnv.line(5.5*inch,8.5*inch,5.5*inch,2.7*inch)
        row_gap=0.6
        line_y=7.9
        cnv.setFont("Times-Roman", 18)
        for row in resultado:
            cnv.drawString(1*inch,line_y*inch,str(row[0]))
            cnv.drawString(2.3 * inch, line_y * inch, str(row[1]))
            cnv.drawString(5.7 * inch, line_y * inch, "R$ "+str(row[2])+"0")
            line_y=line_y-row_gap
        cnv.setFillColorRGB(0, 0, 1)
        cnv.setFont("Helvetica", 20)
        cnv.setFont("Helvetica", 14)
        cnv.setStrokeColorRGB(0.1, 0.8, 0.1)
        cnv.setFillColorRGB(0, 0, 1)  # font colour
        cnv.drawImage("static/images/hamburguer.png", 0 * inch, 9.3 * inch)
        cnv.drawString(0, 9 * inch, "Acesso Restrito")
        cnv.drawString(0, 8.7 * inch, "Rio de Janeiro - RJ")
        cnv.setFillColorRGB(0, 0.5, 1)  # font colour
        cnv.drawString(2.5 * inch, 8.7 * inch, "Relatório Produtos")
        cnv.setFillColorRGB(0, 0, 0)  # font colour
        cnv.line(0, 8.6 * inch, 7.3 * inch, 8.6 * inch)
        dt = date.today().strftime('%d/%m/%Y')
        cnv.drawString(5.6 * inch, 8.7 * inch, dt)
        cnv.setFont("Helvetica", 8)
        cnv.line(0, -0.7 * inch, 6.8 * inch, -0.7 * inch)
        cnv.setFillColorRGB(1, 0, 0)
        cnv.drawString(6.4, -0.9 * inch, u"\u00A9" + "Sistema Hamburgueria")
        cnv.rotate(45)
        cnv.setFillColorCMYK(0, 0, 0, 0.08)
        cnv.setFont("Helvetica", 100)
        cnv.rotate(-45)
        cnv.save()
        flash("Relatório Gerado com Sucesso","alert-success")
    return render_template('relatorioprodutos.html',form_relatorioProdutos=form_relatorioProdutos)
@app.route("/deletarproduto/<id>")
def deletarproduto(id:str):
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.SSCursor)
        cursor.execute(f'delete from produto where id={int(id)}')
        flash("Produto Excluído com Sucesso","alert-success")
    except:
        flash("Erro ao deletar produto", "alert-danger")
    finally:
        mysql.connection.commit()
        cursor.close()
    return redirect("/consultarproduto")
@app.route("/atualizarproduto/<id>/<nome>/<descricao>/<preco>",methods=['GET','POST'])
def atualizarproduto(id:str,nome:str,descricao:str,preco:str):
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    form_atualizarproduto=FormAtualizarProduto()
    form_atualizarproduto.nome.data=nome
    form_atualizarproduto.descricao.data = descricao
    form_atualizarproduto.preco.data =preco
    if form_atualizarproduto.validate_on_submit():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.SSCursor)
            cursor.execute(f'update produto set Nome="{request.form['nome']}", Descricao="{request.form['descricao']}", Preco={float(request.form['preco'])} where id={int(id)}')
            flash("Produto Atualizado com Sucesso", "alert-success")
        except:
            flash("Erro ao Atualizar produto", "alert-danger")
        finally:
            mysql.connection.commit()
            cursor.close()
        return redirect("/consultarproduto")
    return render_template('/atualizarproduto.html',form_atualizarproduto=form_atualizarproduto)
@app.route("/cadastrarfornecedores",methods=['GET','POST'])
def cadastrarfornecedores():
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    form_cadastrarfornecedores=FormCadastrarFornecedores()
    if form_cadastrarfornecedores.validate_on_submit() and 'btn_buscarcep' in request.form:
        if request.form['cep']!="":
            try:
                link = f"https://viacep.com.br/ws/{request.form['cep']}/json"
                requisicao=requests.get(link)
                print(requisicao.json())
                form_cadastrarfornecedores.logradouro.data=requisicao.json()['logradouro']
                form_cadastrarfornecedores.bairro.data = requisicao.json()['bairro']
                form_cadastrarfornecedores.cidade.data = requisicao.json()['localidade']
                form_cadastrarfornecedores.estado.data = requisicao.json()['uf']
                form_cadastrarfornecedores.complemento.data = requisicao.json()['complemento']
            except:
                flash("CEP Inexistente", "alert-danger")
                form_cadastrarfornecedores.cep.data=""
        else:
            flash("CEP Vazio", "alert-danger")
    if form_cadastrarfornecedores.validate_on_submit() and 'btn_cadastrar' in request.form:
        if procedimentos.validar_cpnj(request.form['cnpj'])==True:
            try:
                cursor=mysql.connection.cursor(MySQLdb.cursors.SSCursor)
                cursor.execute(f'select *from fornecedores where Nome= "{request.form['nome']}" and CNPJ="{request.form['cnpj']}"')
                resultado=cursor.fetchall()
                if resultado:
                    flash("Erro ao Inserir Fornecedor, Fornecedor Previamente Cadastrado")
                else:
                    cursor.execute('insert into fornecedores (Nome,Telefone,CNPJ,CEP,Logradouro,Numero,Bairro,Cidade,Estado,Complemento) values ("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}")'.format(request.form['nome'],request.form['telefone'],request.form['cnpj'],request.form['cep'],request.form['logradouro'],request.form['numero'],request.form['bairro'],request.form['cidade'],request.form['estado'],request.form['complemento']))
                    flash("Cadastro de Fornecedor Realizado com Sucesso","alert-success")
            except Exception as e:
                print(e)
            finally:
                mysql.connection.commit()
                cursor.close()
        else:
            flash("CNPJ Informado é Inválido","alert-danger")
    return render_template("/cadastrarfornecedores.html",form_cadastrarfornecedores=form_cadastrarfornecedores)

@app.route('/consultarfornecedores',methods=['GET','POST'])
def consultarfornecedores():
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    form_consultarfornecedores=FormConsultarFornecedores()
    try:
        cursor=mysql.connection.cursor(MySQLdb.cursors.SSCursor)
        cursor.execute('select ID,Nome,Telefone,CNPJ,CEP from fornecedores')
        resultado=cursor.fetchall()
    except:
        resultado=["#"]
        flash("Erro no Carregamento","alert-danger")
    finally:
        mysql.connection.commit()
        cursor.close()
    if form_consultarfornecedores.validate_on_submit():
        cnpj=request.form['cnpj']
        try:
            cursor=mysql.connection.cursor(MySQLdb.cursors.SSCursor)
            cursor.execute(f'select ID,Nome,Telefone,CNPJ,CEP from fornecedores where CNPJ like "{cnpj}%"')
            resultado=cursor.fetchall()
            if resultado:
                pass
            else:
                flash("Produto Não Cadastrado","alert-danger")
        except:
            resultado = ["#"]
            flash("Erro no Carregamento", "alert-danger")
        finally:
            mysql.connection.commit()
            cursor.close()
    return render_template('consultarfornecedores.html',form_consultarfornecedores=form_consultarfornecedores,resultado=resultado)
@app.route("/deletarfornecedores/<id>")
def deletarfornecedores(id:str):
    try:
        if session['loggedin'] != True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!", "alert-danger")
        return redirect("/login")
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.SSCursor)
        cursor.execute(f'delete from fornecedores where ID={int(id)}')
        flash("Fornecedor Excluído com Sucesso","alert-success")
    except:
        flash("Erro ao deletar produto", "alert-danger")
    finally:
        mysql.connection.commit()
        cursor.close()
    return redirect("/consultarfornecedores")
@app.route("/atualizarfornecedores/<id>",methods=['GET','POST'])
def atualizarfornecedores(id:str):
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    form_atualizarfornecedores=FormAtualizarFornecedores()
    try:
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute(
            f'select Logradouro,Numero,Bairro,Cidade,Estado,Complemento,Telefone,CNPJ,CEP,Nome from fornecedores where ID={int(id)}')
        resultado=cursor1.fetchone()
        if resultado:
            form_atualizarfornecedores.logradouro.data=resultado['Logradouro']
            form_atualizarfornecedores.numero.data = resultado["Numero"]
            form_atualizarfornecedores.bairro.data= resultado["Bairro"]
            form_atualizarfornecedores.cidade.data = resultado["Cidade"]
            form_atualizarfornecedores.estado.data = resultado["Estado"]
            form_atualizarfornecedores.complemento.data = resultado["Complemento"]
            form_atualizarfornecedores.telefone.data = resultado["Telefone"]
            form_atualizarfornecedores.cnpj.data = resultado["CNPJ"]
            form_atualizarfornecedores.cep.data = resultado["CEP"]
            form_atualizarfornecedores.nome.data = resultado["Nome"]
    except Exception as e:
        flash("Erro ao Buscar Dados do fornecedor", "alert-danger")
        print(e)
    finally:
        mysql.connection.commit()
        cursor1.close()
    if form_atualizarfornecedores.validate_on_submit() and 'btn_atualizar' in request.form:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.SSCursor)
            cursor.execute(f'update fornecedores set Nome="{request.form['nome']}", Telefone="{request.form['telefone']}", CNPJ="{request.form['cnpj']}",CEP="{request.form["cep"]}",Logradouro="{request.form["logradouro"]}",Numero="{request.form["numero"]}",Bairro="{request.form["bairro"]}",Cidade="{request.form["cidade"]}",Estado="{request.form["estado"]}",Complemento="{request.form["complemento"]}" where ID={int(id)}')
            flash("Fornecedor Atualizado com Sucesso", "alert-success")
        except:
            flash("Erro ao Atualizar fornecedor", "alert-danger")
        finally:
            mysql.connection.commit()
            cursor.close()
        return redirect("/consultarfornecedores")
    if form_atualizarfornecedores.validate_on_submit() and 'btn_buscarcep' in request.form:
        if request.form['cep']!="":
            try:
                cep=request.form['cep']
                nome=request.form['nome']
                telefone=request.form['telefone']
                cnpj=request.form['cnpj']
                numero=request.form['numero']
                link = f"https://viacep.com.br/ws/{request.form['cep']}/json"
                requisicao=requests.get(link)
                print(requisicao.json())
                form_atualizarfornecedores.nome.data = nome
                form_atualizarfornecedores.telefone.data = telefone
                form_atualizarfornecedores.cnpj.data = cnpj
                form_atualizarfornecedores.numero.data = numero
                form_atualizarfornecedores.cep.data=cep
                form_atualizarfornecedores.logradouro.data=requisicao.json()['logradouro']
                form_atualizarfornecedores.bairro.data = requisicao.json()['bairro']
                form_atualizarfornecedores.cidade.data = requisicao.json()['localidade']
                form_atualizarfornecedores.estado.data = requisicao.json()['uf']
                form_atualizarfornecedores.complemento.data = requisicao.json()['complemento']
            except:
                flash("CEP Inexistente", "alert-danger")
                form_atualizarfornecedores.cep.data=""
        else:
            flash("CEP Vazio", "alert-danger")
    return render_template('/atualizarfornecedores.html',form_atualizarfornecedores=form_atualizarfornecedores)
@app.route("/vendas",methods=['GET','POST'])
def vendas():
    try:
        if session['loggedin'] != True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!", "alert-danger")
        return redirect("/login")
    try:
        cursor=mysql.connection.cursor(MySQLdb.cursors.SSCursor)
        cursor.execute('select ID,Nome,Preco from produto')
        resultado=cursor.fetchall()
    except:
        resultado=["#"]
        flash("Erro no Carregamento","alert-danger")
    finally:
        mysql.connection.commit()
        cursor.close()
    return render_template("/vendas.html",resultado=resultado)
@app.route("/finalizacaovendas/<total>", methods=['GET', 'POST'])
def finalizacaovendas(total:str):
    try:
        if session['loggedin']!=True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!","alert-danger")
        return redirect("/login")
    formfinalizacaovendas=FormFinalizacaoVendas()
    formfinalizacaovendas.total.data="R$ "+total
    data_atual=datetime.now()
    data_em_texto = data_atual.strftime('%d/%m/%Y')
    hora_em_texto=data_atual.strftime('%H:%M:%S')
    if formfinalizacaovendas.validate_on_submit() and "btn_finalizacao" in request.form:
        print("Entrei nesse método")
        if float(total)<float(request.form["valor_cliente"]):
            troco=float(request.form["valor_cliente"])-float(total)
            flash("O Seu troco é: " +str(math.floor(troco*100)/100),"alert-success")
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.SSCursor)
                cursor.execute(
                        'insert into vendas (Data,Hora,Total,Valor_Cliente,Troco,CPF_Entrada) values ("{}","{}","{}","{}","{}","{}")'.format(
                            data_em_texto, hora_em_texto, float(total), float(request.form["valor_cliente"]),
                            troco, str(session['id'])))
                flash("Venda Finalizada com Sucesso", "alert-success")
                return redirect("/")
            except Exception as e:
                print(e)
            finally:
                mysql.connection.commit()
                cursor.close()
        else:
            flash("O Valor é inferior ao Total","alert-danger")
    return render_template("/finalizacaovendas.html",formfinalizacaovendas=formfinalizacaovendas)
@app.route("/relatoriousuarios", methods=['GET', 'POST'])
def relatoriousuarios():
    form_relatorioUsuarios=FormRelatorioUsuarios()
    try:
        if session['loggedin'] != True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!", "alert-danger")
        return redirect("/login")
    if form_relatorioUsuarios.validate_on_submit():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.SSCursor)
            cursor.execute(f'SELECT COUNT(v.CPF_Entrada) AS contagem, e.CPF, e.Nome FROM Entrada e LEFT JOIN Vendas v ON e.CPF = v.CPF_Entrada WHERE e.Nome LIKE "{request.form['usuario']}%" GROUP BY e.CPF, e.Nome')
            resultado = cursor.fetchall()
            if resultado:
                pass
            else:
                flash("Usuário Não Cadastrado", "alert-danger")
        except:
            resultado = ["#"]
            flash("Erro no Carregamento", "alert-danger")
        finally:
            mysql.connection.commit()
            cursor.close()
        file = f"relatoriousuario-{date.today().strftime('%d-%m-%Y')}.pdf"
        cnv = canvas.Canvas("C:\\Users\\aluno\\Downloads\\" + file, pagesize=letter)
        cnv.setFillColorRGB(1, 0, 0)
        cnv.setFont("Helvetica", 40)
        cnv.setFillColorRGB(0, 0, 0)
        cnv.setFont("Times-Roman", 22)
        cnv.drawRightString(1.3 * inch, 8.3 * inch, 'CPF:')
        cnv.drawRightString(3.5 * inch, 8.3 * inch, 'Nome:')
        cnv.drawRightString(6.8 * inch, 8.3 * inch, 'Vendas:')
        cnv.setStrokeColorCMYK(0, 0, 0, 1)
        cnv.line(2 * inch, 8.5 * inch, 2 * inch, 2.7 * inch)
        cnv.line(5.5 * inch, 8.5 * inch, 5.5 * inch, 2.7 * inch)
        row_gap = 0.6
        line_y = 7.9
        cnv.setFont("Times-Roman", 18)
        for row in resultado:
            formatopalavra = str(row[1])[9:11]
            cpf = str(row[0])[0:3] + ".***.***-" + formatopalavra
            cnv.drawString(0.3 * inch, line_y * inch, cpf)
            cnv.drawString(2.3 * inch, line_y * inch, str(row[2]))
            cnv.drawString(6.2 * inch, line_y * inch,str(row[0]))
            line_y = line_y - row_gap
        cnv.setFillColorRGB(0, 0, 1)
        cnv.setFont("Helvetica", 20)
        cnv.setFont("Helvetica", 14)
        cnv.setStrokeColorRGB(0.1, 0.8, 0.1)
        cnv.setFillColorRGB(0, 0, 1)  # font colour
        cnv.drawImage("static/images/hamburguer.png", 0 * inch, 9.3 * inch)
        cnv.drawString(0, 9 * inch, "Acesso Restrito")
        cnv.drawString(0, 8.7 * inch, "Rio de Janeiro - RJ")
        cnv.setFillColorRGB(0, 0.5, 1)  # font colour
        cnv.drawString(2.5 * inch, 8.7 * inch, "Relatório Usuários")
        cnv.setFillColorRGB(0, 0, 0)  # font colour
        cnv.line(0, 8.6 * inch, 7.3 * inch, 8.6 * inch)
        dt = date.today().strftime('%d/%m/%Y')
        cnv.drawString(5.6 * inch, 8.7 * inch, dt)
        cnv.setFont("Helvetica", 8)
        cnv.line(0, -0.7 * inch, 6.8 * inch, -0.7 * inch)
        cnv.setFillColorRGB(1, 0, 0)
        cnv.drawString(6.4, -0.9 * inch, u"\u00A9" + "Sistema Hamburgueria")
        cnv.rotate(45)
        cnv.setFillColorCMYK(0, 0, 0, 0.08)
        cnv.setFont("Helvetica", 100)
        cnv.rotate(-45)
        cnv.save()
        flash("Relatório Gerado com Sucesso", "alert-success")
    return render_template("/relatoriousuarios.html",form_relatorioUsuarios=form_relatorioUsuarios)
@app.route("/relatoriofornecedores", methods=['GET', 'POST'])
def relatoriofornecedores():
    form_relatoriofornecedores=FormRelatorioFornecedores()
    try:
        if session['loggedin'] != True:
            flash("Você Precisa Estar Logado para acessar a Página!")
            return redirect("/login")
    except:
        flash("Você Precisa Estar Logado para acessar a Página!", "alert-danger")
        return redirect("/login")
    if form_relatoriofornecedores.validate_on_submit():
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.SSCursor)
            cursor.execute(
                f'SELECT ID,Nome,Telefone from fornecedores where CNPJ like "{request.form['cnpj']}%"')
            resultado = cursor.fetchall()
            if resultado:
                pass
            else:
                flash("Fornecedor Não Cadastrado", "alert-danger")
        except:
            resultado = ["#"]
            flash("Erro no Carregamento", "alert-danger")
        finally:
            mysql.connection.commit()
            cursor.close()
        file = f"relatoriofornecedor-{date.today().strftime('%d-%m-%Y')}.pdf"
        cnv = canvas.Canvas("C:\\Users\\aluno\\Downloads\\" + file, pagesize=letter)
        cnv.setFillColorRGB(1, 0, 0)
        cnv.setFont("Helvetica", 40)
        cnv.setFillColorRGB(0, 0, 0)
        cnv.setFont("Times-Roman", 22)
        cnv.drawRightString(1.3 * inch, 8.3 * inch, 'ID:')
        cnv.drawRightString(3.5 * inch, 8.3 * inch, 'Nome:')
        cnv.drawRightString(7.2 * inch, 8.3 * inch, 'Telefone:')
        cnv.setStrokeColorCMYK(0, 0, 0, 1)
        cnv.line(2 * inch, 8.5 * inch, 2 * inch, 2.7 * inch)
        cnv.line(5.5 * inch, 8.5 * inch, 5.5 * inch, 2.7 * inch)
        row_gap = 0.6
        line_y = 7.9
        cnv.setFont("Times-Roman", 16)
        for row in resultado:
            cnv.drawString(1 * inch, line_y * inch, str(row[0]))
            cnv.drawString(2.3 * inch, line_y * inch, str(row[1]))
            cnv.drawString(6 * inch, line_y * inch, str(row[2]))
            line_y = line_y - row_gap
        cnv.setFillColorRGB(0, 0, 1)
        cnv.setFont("Helvetica", 20)
        cnv.setFont("Helvetica", 14)
        cnv.setStrokeColorRGB(0.1, 0.8, 0.1)
        cnv.setFillColorRGB(0, 0, 1)  # font colour
        cnv.drawImage("static/images/hamburguer.png", 0 * inch, 9.3 * inch)
        cnv.drawString(0, 9 * inch, "Acesso Restrito")
        cnv.drawString(0, 8.7 * inch, "Rio de Janeiro - RJ")
        cnv.setFillColorRGB(0, 0.5, 1)  # font colour
        cnv.drawString(2.5 * inch, 8.7 * inch, "Relatório Fornecedores")
        cnv.setFillColorRGB(0, 0, 0)  # font colour
        cnv.line(0, 8.6 * inch, 7.3 * inch, 8.6 * inch)
        dt = date.today().strftime('%d/%m/%Y')
        cnv.drawString(5.6 * inch, 8.7 * inch, dt)
        cnv.setFont("Helvetica", 8)
        cnv.line(0, -0.7 * inch, 6.8 * inch, -0.7 * inch)
        cnv.setFillColorRGB(1, 0, 0)
        cnv.drawString(6.4, -0.9 * inch, u"\u00A9" + "Sistema Hamburgueria")
        cnv.rotate(45)
        cnv.setFillColorCMYK(0, 0, 0, 0.08)
        cnv.setFont("Helvetica", 100)
        cnv.rotate(-45)
        cnv.save()
        flash("Relatório Gerado com Sucesso", "alert-success")
    return render_template("/relatoriofornecedores.html",form_relatoriofornecedores=form_relatoriofornecedores)
@socketio.on('key_pressed')
def handle_key_pressed(data):
    key=data['key']
    print(f"Tecla Pressionada: {key}")
    emit('key_response',{'key':key})
    total_string = data.get('total_string', "")
    try:
        print(total_string)
    except ValueError:
        flash("Total Inválido", "alert-danger")
    if(key=="F2"):
        print('entrei no if')
        emit('redirect', {f'url': f'/finalizacaovendas/{total_string}'})
if __name__ =='__main__':
    app.run(debug=True)