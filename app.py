# Importação das bibliotecas

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
db = SQLAlchemy(app)

class Product(db.Model):
    #Nullable como false, torná o campo obrigatório
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    #O Text ao invés do String não restringe a quantidade de caracteres
    description = db.Column(db.Text, nullable=True)
    #Definindo uma rota raíz (página inicial) e a função que será executado ao requisitar
