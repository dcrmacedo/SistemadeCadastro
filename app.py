from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# Configuração do Flask e do SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'clients.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

@app.route('/api/clients/<int:client_id>', methods=['PUT', 'DELETE'])
def handle_single_client(client_id):
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)