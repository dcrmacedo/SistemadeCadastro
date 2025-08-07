import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

# Configuração do Flask e do SQLAlchemy
app = Flask(__name__)

# Obter URL do banco de dados da variável de ambiente
database_url = os.environ.get('DATABASE_URL')

# Se não houver DATABASE_URL (ambiente local), usar SQLite como fallback
if not database_url:
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_url = 'sqlite:///' + os.path.join(basedir, 'clients.db')

# Ajustar formato da URL para PostgreSQL (se necessário)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

# Configurações do SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300
}

db = SQLAlchemy(app)

# Modelo do banco de dados para os clientes
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    date = db.Column(db.String(10), nullable=False)
    budgetCode = db.Column(db.String(50), nullable=False)
    orderCode = db.Column(db.String(50), nullable=False)
    orderUrl = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cpf': self.cpf,
            'date': self.date,
            'budgetCode': self.budgetCode,
            'orderCode': self.orderCode,
            'orderUrl': self.orderUrl
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clients', methods=['GET', 'POST'])
def handle_clients():
    try:
        if request.method == 'POST':
            data = request.json
            if Client.query.filter_by(cpf=data['cpf']).first():
                return jsonify({'message': 'Este CPF já está cadastrado.'}), 409
            new_client = Client(
                name=data['name'],
                cpf=data['cpf'],
                date=data['date'],
                budgetCode=data['budgetCode'],
                orderCode=data['orderCode'],
                orderUrl=data.get('orderUrl')
            )
            db.session.add(new_client)
            db.session.commit()
            return jsonify(new_client.to_dict()), 201
        
        if request.method == 'GET':
            clients = Client.query.all()
            return jsonify([client.to_dict() for client in clients])

    except Exception as e:
        print(f"Erro na rota /api/clients: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500


@app.route('/api/clients/<int:client_id>', methods=['PUT', 'DELETE'])
def handle_single_client(client_id):
    try:
        client = Client.query.get_or_404(client_id)
        if request.method == 'PUT':
            data = request.json
            client.name = data['name']
            client.cpf = data['cpf']
            client.budgetCode = data['budgetCode']
            client.orderCode = data['orderCode']
            client.orderUrl = data.get('orderUrl')
            db.session.commit()
            return jsonify(client.to_dict())
        
        if request.method == 'DELETE':
            db.session.delete(client)
            db.session.commit()
            return jsonify({'message': 'Cliente excluído com sucesso'}), 200
    except Exception as e:
        print(f"Erro na rota /api/clients/{client_id}: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500


if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Banco de dados inicializado com sucesso!")
            print(f"Usando banco de dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 
