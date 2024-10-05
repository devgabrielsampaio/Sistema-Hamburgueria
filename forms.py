from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,SelectField
from wtforms.validators import DataRequired,Length,Email,EqualTo


class FormCriarConta(FlaskForm):
    username= StringField("Nome de Usuário",validators=[DataRequired()])
    email= StringField("E-mail",validators=[DataRequired(),Email()])
    cpf=StringField("CPF",validators=[Length(11,11),DataRequired()])
    senha= PasswordField("Senha",validators=[DataRequired(),Length(6,20)])
    confirmacao= PasswordField("Confirmação",validators=[DataRequired(),EqualTo('senha')])
    genero=SelectField('Gênero',choices=[('Masculino','Masculino'),('Feminino','Feminino'),('Outros','Outros')])
    botao_criarconta= SubmitField("Criar Conta",validators=[DataRequired()])

class FormLogin(FlaskForm):
    cpf = StringField("CPF",validators=[Length(11,11),DataRequired()])
    senha = PasswordField("Senha",validators=[DataRequired(),Length(6,20)])
    lembrar_dados=BooleanField("Lembrar Dados de Acesso")
    botao_fazerlogin = SubmitField("Login")
class FormConsultarProduto(FlaskForm):
    nome=StringField("Nome:")
    botao_consultar=SubmitField("Consultar",validators=[DataRequired()])
class FormRelatorioProdutos(FlaskForm):
    nome = StringField("Nome:")
    botao_gerarRelatorio = SubmitField("Gerar Relatório", validators=[DataRequired()])
class FormCadastrarProduto(FlaskForm):
    nome=StringField("Nome:",validators=[DataRequired(),Length(10,75)])
    descricao=StringField("Descrição:",validators=[DataRequired(),Length(10,117)])
    preco=StringField("Preço:",validators=[DataRequired()])
    btn_cadastrar=SubmitField("Cadastrar",validators=[DataRequired()])
class FormAtualizarProduto(FlaskForm):
    nome = StringField("Nome:", validators=[DataRequired(), Length(10, 75)])
    descricao = StringField("Descrição:", validators=[DataRequired(), Length(10, 117)])
    preco = StringField("Preço:", validators=[DataRequired()])
    btn_atualizar=SubmitField("Atualizar",validators=[DataRequired()])
class FormCadastrarFornecedores(FlaskForm):
    nome=StringField("Nome:",validators=[DataRequired(), Length(10, 75)])
    telefone=StringField("Telefone:",validators=[DataRequired()])
    cnpj=StringField("CNPJ:",validators=[DataRequired(), Length(18, 18)])
    cep=StringField("CEP:")
    logradouro=StringField("Logradouro:")
    numero=StringField("Número:")
    bairro = StringField("Bairro:")
    cidade = StringField("Cidade:")
    estado=StringField("Estado:")
    complemento=StringField("Complemento:")
    btn_cadastrar=SubmitField("Cadastrar")
    btn_buscarcep=SubmitField("Buscar CEP")
class FormConsultarFornecedores(FlaskForm):
    cnpj=StringField("CNPJ:")
    botao_consultar=SubmitField("Consultar")

class FormAtualizarFornecedores(FlaskForm):
    nome = StringField("Nome:", validators=[DataRequired(), Length(10, 75)])
    telefone = StringField("Telefone:", validators=[DataRequired()])
    cnpj = StringField("CNPJ:", validators=[DataRequired(), Length(18, 18)])
    cep = StringField("CEP:")
    logradouro = StringField("Logradouro:")
    numero = StringField("Número:")
    bairro = StringField("Bairro:")
    cidade = StringField("Cidade:")
    estado = StringField("Estado:")
    complemento = StringField("Complemento:")
    btn_atualizar = SubmitField("Atualizar")
    btn_buscarcep = SubmitField("Buscar CEP")
class FormFinalizacaoVendas(FlaskForm):
    total=StringField("Total:")
    valor_cliente=StringField("Valor Cliente")
    btn_finalizacao=SubmitField("Finalizar Venda")
class FormRelatorioUsuarios(FlaskForm):
    usuario = StringField("Usuário:")
    botao_gerarRelatorio = SubmitField("Gerar Relatório", validators=[DataRequired()])
class FormRelatorioFornecedores(FlaskForm):
    cnpj = StringField("CNPJ:", validators=[Length( 0,18)])
    botao_gerarRelatorio = SubmitField("Gerar Relatório", validators=[DataRequired()])