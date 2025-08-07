import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

# Configuração da URL do banco de dados
database_url = os.environ.get('DATABASE_URL', 'sqlite:///clients.db')

# Correção e formatação da URL
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
elif database_url and 'postgresql://' not in database_url and 'sqlite://' not in database_url:
    database_url = f'postgresql://{database_url}'

print(f"Database URL: {database_url}")  # Para debug

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300
}
db = SQLAlchemy(app)

# ... (o resto do seu código permanece igual) ...

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
