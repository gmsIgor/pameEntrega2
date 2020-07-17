

""" 
- Importações 
Flask      -> Classe Flask pra utilizar o framework
request    -> com request que vc pega os dados passados na request (body, querystring, etc..)
              request.json -> retorna o body da requisição como um dicionário
              request.args -> retorna a querystring da requisição. Ex: /users/?idade=15, 
                              request.args retorna um dicionário {'idade':15} ele pega tudo depois do '?'
jsonify    -> serve pra retornar um json, só vai ser utilizado no código aqui pra transformar lista em json
SQLAlchemy -> é a classe pro banco de dados, é a ORM
"""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Cria um objeto da classe Flask, tudo que for utilizar o flask tem que utilizar através do 'app'
app = Flask(__name__)

""" 
Configurações do Banco de Dados
Esse 'app.config' é um dicionário de configuração que tá na classe Flask 
Vamos fazer só com o sqlite mesmo
"""
# Modelo de endereço pro sqlite, assim é criado o banco na própia pasta
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data-dev.db'

# Tem que setar como falso pq não vamos utilizar isso, não vamos precisar ficar monitoriando cada mudança no banco
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JSON_SORT_KEYS"] = False

""" Instancía o banco de dados, é colocado o app como parâmetro assim as configurações
 no dicionário de configurações do app ali em cima são passadas pro banco """
db = SQLAlchemy(app)


class User(db.Model):
    """ 
    Classe que representa uma tabela no banco de dados
    tem que herdar de db.Model pro SQLAlquemy reconhecer.
    """

    # Define o nome da tabela, prática seguida é botar o plural do nome da classe, tudo minúsculo
    __tablename__ = 'users'

    # Pra criar um campo na tabela utilizamos a função Column do db
    # Toda tabela tem que ter um 'id' sempre temos que criar, estou botando como 'primary_key'
    id = db.Column(db.Integer, primary_key=True)
    # nome do usuário como string, não pode ser nulo
    name = db.Column(db.String(20), nullable=False)
    # email como string, não pode ser nulo e tem que ser único
    email = db.Column(db.String(20), unique=True, nullable=False)
    # idade como Integer, valor padrão como '0'
    idade = db.Column(db.Integer, default=0)

    # Aqui temos uma função que retorna um dicionário representando um usuário
    def json(self):
        user_json = {'id': self.id,
                     'name': self.name,
                     'email': self.email,
                     'idade': self.idade}
        return user_json


# Rota para a criação de um usuário
# Se quiser botar outros métodos só adicionar na lista, tipo methods=['POST', 'GET']
# e depois testar cada um com umm 'if request.method == 'GET'', por exemplo
@app.route('/users/', methods=['POST'])
def create():

    data = request.json  # Pegando o body da requisição como um dicionário

    # Pegando cada campo do dicionário, se não for fornecido retorna um 'None'
    name = data.get('name')
    email = data.get('email')
    idade = data.get('idade')

    # Testando pra ver se tem o nome e email na requisição, são campos obrigatórios
    if not name or not email:
        # retorna esse json com o código 400 se não tiver
        # veja que se eu retornar um dicionário ele vai direto como um json, sem precisar do 'jsonify'
        return {'error': 'Dados insuficientes'}, 400

    if User.query.filter_by(email=email).first():
        return {'error': 'email já cadastrado'}, 409
        
    # Crio o usuário, perceba que eu não estou testando pra ver se um usuário com o mesmo email,
    # que deve ser único, já existe, se já existir o banco vai dar um erro de integridade.
    user = User(name=name, email=email, idade=idade)

    # Salvando o usuário no banco
    # Sempre quando eu vou salvar tenho que adicionar na 'session' de ações pro banco fazer
    # posso colocar várias ações, só depois do 'session.commit()' que vai ser executado
    db.session.add(user)
    db.session.commit()

    # Retornando a representação do usuário como dicionário usando a função .json() definida no model
    # Assim é retornado automaticamente como json
    return user.json(), 200


# Rota que retorna uma lista de usuário, vai poder filtrar por idade
@app.route('/users/', methods=['GET'])
def index():

    # Pega a querystring da requisição
    # a querystring é tudo que vem depois do '?' na url
    # ex. /produtos/?cor=azul&tamanho=m cada parâmetro podemos separa com um '&'
    # a querystring seria {'cor':'azul', 'tamanho':'m'}
    data = request.args

    # A ideia aqui é que o endpoint possa ser assim
    # /users/?idade=35-40 ou um /users/?idade=17
    # assim só retornaria usuário com idades entre 35 e 40 anos
    # ou no caso do segundo endpoint usuários com 17 anos

    idade = data.get('idade')  # Pego a 'idade' do dicionário da querystring

    if not idade:  # Vejo se botaram a idade mesmo ou ou só botaram um /users/
        users = User.query.all()  # Se só botaram um /users/ pego todos os usuários no banco
    else:

        # Retorna um array dos elementos separados por '-'
        # Se for, por exemplo, 20-30, retorna ['20', '30']
        # Se for, por exemplo, 20, só quer uma idade especifica, retorna ['20']
        idade = idade.split('-')

        # Testo o tamanho do array pra ver se é o primeiro ou segundo caso, X-Y ou só X
        if len(idade) == 1:
            # Se for só 1 o tamanho quer dizer que o usuário só botou, por exemplo, /users/?idade=19
            # Assim eu filtro só com usuários dessa idade
            # Perceba que eu trato a idade como array que é o retorno do idade.split('-') definido anteriormente
            users = User.query.filter_by(idade=idade[0])
        else:
            # Aqui é se o tipo for /users/?idade=X-Y, o array idade é ['X', 'Y']
            # Eu filtro pra idades maiores ou iguais a 'X' e menores ou iguis a 'Y'
            # Perceba que aqui eu usei o filter e lá em cima eu usei o filter_by
            # A diferença é que no filter_by só consigo botar um igual mesmo, igual um parâmetro de função mesmo tipo (nome='leandro')
            # No filter eu consigo botar uma expressão, tipo, (User.idade > X)
            # Veja que eu uso o 'db.and_' pra falar que as duas expressões tem que valer
            # outra opção seria um 'db.or_' pra falar que qualquer uma poderia valer
            # Perceba também que tenho que utilizar o nome da classe junto, tipo User.idade
            users = User.query.filter(
                db.and_(User.idade >= idade[0], User.idade <= idade[1]))

    # Como no users tenho uma lista de usuários tenho que usar o jsonify pra retornar como json
    # Essa expressão dentro do jsonify cria uma lista da seguinte, pode ser lida da seguinte forma:
    # pra cada 'user' dentro da lista 'users' pega o 'user.json()' dele e coloca numa lista
    return jsonify([user.json() for user in users]), 200


# Rota que retorna um usuário pelo id dele
# Perceba que tem que botar entre <> o id
# e tem que botar como parâmetro da função também
# eu especifiquei o id como integer ali com o 'int:'
# se eu deixar ser nada <id> ele entende como string por padrão
@app.route('/users/<int:id>', methods=['GET'])
def user_detail(id):

    # Testo pra ver se é um GET a requisição
    # o tipo vem no request.method
    if request.method == 'GET':
        # Pega um usuário pelo 'id' ou retorna um erro 404
        user = User.query.get_or_404(id)
        # retorna o usuário como json
        return user.json(), 200

@app.route('/users/<int:id>', methods=['PUT'])
def user_change(id):

    data = request.json

    name = data.get('name')
    email = data.get('email')
    idade = data.get('idade')

    if not name or not email or not idade:
        return {'error': 'Dados insuficientes'}, 400
    
    if User.query.filter_by(email=email).first():
        return {'error': 'email já cadastrado'}, 409

    user = User.query.filter_by(id=id).first() #.update(User(id=id,nome=name,email=email,idade=idade))
    user.name = name
    user.email = email
    user.idade = idade

    db.session.commit()

    return user.json(), 200

@app.route('/users/<int:id>', methods=['PATCH'])
def user_update(id):

    data = request.json
    user = User.query.filter_by(id=id).first()

    name = data.get('name')
    email = data.get('email')
    idade = data.get('idade')

    if User.query.filter_by(email=email).first():
        return {'error': 'email já cadastrado'}, 409

    if name:
         user.name = name

    if email:
         user.email = email

    if idade:
         user.idade = idade

    db.session.commit()
    return user.json(), 200



@app.route('/users/<int:id>', methods=['DELETE'])
def user_delete(id):
    user = User.query.filter_by(id=id).delete()
    db.session.commit()
    return user.json(), 200



if __name__ == '__main__':
    app.run(debug=True)
