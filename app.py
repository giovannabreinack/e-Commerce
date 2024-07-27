# Importação das bibliotecas
from flask import Flask, request, jsonify
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
    
@app.route('/api/products/add', methods=["POST"])
def add_product():

    data = request.json


    if 'name' in data and 'price' in data:
     product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
     db.session.add(product)
     db.session.commit()
     return jsonify({"message": "Produto adicionado com sucesso!"})
    return jsonify({"message": "Dados do produto inválidos"}), 400


@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product != None:
       db.session.delete(product)
       db.session.commit()
       return jsonify({"message": "Produto deletado com sucesso!"})
    return jsonify({"message": "Produto não encontrado"}), 404