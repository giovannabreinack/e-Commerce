# Importação das bibliotecas
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = "python_ecommerce_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

# Criação da tabela de Usuário no BD
class User(db.Model, UserMixin):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(80), nullable=False, unique=True)
   password = db.Column(db.String(80), nullable=False)
   cart = db.relationship('CartItem', backref='user', lazy=True)

# Criação do banco de dados - Tabela de Produtos
class Product(db.Model):
    #Nullable como false, torná o campo obrigatório
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    #O Text ao invés do String não restringe a quantidade de caracteres
    description = db.Column(db.Text, nullable=True)

# Itens do carrinho de compras
class CartItem(db.Model):
 id = db.Column(db.Integer, primary_key=True)
 user_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
 product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# Autenticação
@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))

# Rota de LogIn
@app.route('/login', methods=["POST"])
def login():
   data = request.json
   data.get("username")
   user = User.query.filter_by(username=data.get("username")).first()
   if user != None and data.get("password") == user.password:
       login_user(user)
       return jsonify({"message:" "Login feito com sucesso!"})
   return jsonify({"message": "Não Autorizado. Credenciais Inválidas"}), 401

# Rota de LogOut
@app.route('/logout', methods=["POST"])
@login_required
def logout():
   logout_user()
   return jsonify({"message": "Logout feito com sucesso!"})

# Adicionar Produtos   
@app.route('/api/products/add', methods=["POST"])
@login_required
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
     product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
     db.session.add(product)
     db.session.commit()
     return jsonify({"message": "Produto adicionado com sucesso!"})
    return jsonify({"message": "Dados do produto inválidos"}), 400

# Deletar produtos
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product != None:
       db.session.delete(product)
       db.session.commit()
       return jsonify({"message": "Produto deletado com sucesso!"})
    return jsonify({"message": "Produto não encontrado"}), 404

# Visualização dos produtos
@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_product_details(product_id):
   product = Product.query.get(product_id)
   if product:
      return jsonify({"id": product.id, "name": product.name, "price": product.price, "description": product.description})
   return jsonify ({"message": "Produto não encontrado!"}), 404
     
# Atualização dos produtos
@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):
   product = Product.query.get(product_id)
   if not product:
      return jsonify({"message": "Produto não encontrado"}), 404
   
   data = request.json

   if 'name' in data:
      product.name = data['name']

   if 'price' in data:
      product.price = data['price']

   if 'description' in data:
      product.description = data['description']

   db.session.commit()
   return jsonify({"message": "Produto atualizado com sucesso!"})

# Recuperar a lista de produtos
@app.route('/api/products', methods=["GET"])
def get_products():
   products = Product.query.all()
   product_list = []
   for product in products:
      product_data = {
         "id": product.id,
         "name": product.name,
         "price": product.price
      }
      product_list.append(product_data)
      return jsonify(product_list)

# Adicionar itens no carrinho de compras
@app.route('/api/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
   user = User.query.get(int(current_user.id))
   product = Product.query.get(product_id)
   if user and product:
    cart_item = CartItem(user_id=user.id, product_id=product.id)
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({"message": "Item adicionado no carrinho com sucesso!"})
   return jsonify({"message": "Falha ao adicionar o produto no carrinho"}), 400

# Remover itens do carrinho
app.route('/api/cart/remove/<int:product_id>', methods=["DELETE"])
@login_required
def remove_from_cart(product_id):
   cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
   if cart_item:
      db.session.delete(cart_item)
      db.session.commit()
      return jsonify({"message": "Produto removido do carrinho com sucesso!"})
   return jsonify({"message": "Falha ao remover o produto do carrinho"}), 400

# Visualizar seu carrinho de compras
@app.route('/api/cart', methods=['GET'])
@login_required
def view_cart():
   user = User.query.get(int(current_user.id))
   cart_items = user.cart
   cart_content= []
   for cart_item in cart_items:
      product = Product.query.get(cart_item.product_id)
      cart_content.append({
         "id": cart_item.id,
         "user_id": cart_item.user_id,
         "product_id": cart_item.product_id,
         "product_name": product,
         "product_price": product.price
      })
   return jsonify(cart_content)

# CheckOut e limpeza do carrinho
@app.route('/api/cart/checkout', methods=["POST"])
@login_required
def checkout():
   user = User.query.get(int(current_user.id))
   cart_items = user.cart
   for cart_item in cart_items:
      db.session.delete(cart_item)
      db.session.commit()
   return jsonify({"message": "CheckOut feito com sucesso. Carrinho vazio"})





   