from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    cart_items = db.relationship('CartItem', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    stock = db.Column(db.Integer, nullable=False)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

def add_products():
    products = [
        {
            'name': 'Rice',
            'price': 45.00,
            'description': 'Premium quality rice, perfect for daily cooking.',
            'image': 'rice.jpg',
            'stock': 100
        },
        {
            'name': 'Milk',
            'price': 32.00,
            'description': 'Fresh full cream milk, rich in calcium.',
            'image': 'milk.jpg',
            'stock': 50
        },
        {
            'name': 'Shampoo',
            'price': 180.00,
            'description': 'Gentle hair care shampoo for all hair types.',
            'image': 'shampoo.jpg',
            'stock': 30
        },
        {
            'name': 'Sunflower Oil',
            'price': 120.00,
            'description': 'Pure sunflower oil for healthy cooking.',
            'image': 'sunflower-oil.jpg',
            'stock': 40
        },
        {
            'name': 'Mango',
            'price': 60.00,
            'description': 'Fresh and sweet mangoes.',
            'image': 'mango.jpg',
            'stock': 75
        },
        {
            'name': 'Bread',
            'price': 35.00,
            'description': 'Fresh white bread, perfect for breakfast.',
            'image': 'bread.jpg',
            'stock': 45
        },
        {
            'name': 'Orange',
            'price': 80.00,
            'description': 'Fresh juicy oranges, rich in vitamin C.',
            'image': 'orange.jpg',
            'stock': 70
        },
        {
            'name': 'Biscuits',
            'price': 20.00,
            'description': 'Crispy and delicious biscuits.',
            'image': 'biscuit.jpg',
            'stock': 120
        },
        {
            'name': 'Grapes',
            'price': 150.00,
            'description': 'Fresh green grapes, sweet and juicy.',
            'image': 'graps.jpg',
            'stock': 40
        },
        {
            'name': 'Colgate Toothpaste',
            'price': 85.00,
            'description': 'Fresh breath and strong teeth.',
            'image': 'colgate.jpg',
            'stock': 60
        },
        {
            'name': 'Potatoes',
            'price': 25.00,
            'description': 'Fresh potatoes for cooking.',
            'image': 'potetos.jpg',
            'stock': 150
        },
        {
            'name': 'Onions',
            'price': 35.00,
            'description': 'Fresh onions for cooking.',
            'image': 'onion.jpg',
            'stock': 100
        },
        {
            'name': 'Salt',
            'price': 20.00,
            'description': 'Pure iodized salt.',
            'image': 'salt.jpg',
            'stock': 200
        },
        {
            'name': 'Sugar',
            'price': 45.00,
            'description': 'Pure white sugar.',
            'image': 'sugar.jpg',
            'stock': 150
        },
        {
            'name': 'Toor Dal',
            'price': 120.00,
            'description': 'Premium quality toor dal.',
            'image': 'toor dal.jpg',
            'stock': 60
        },
        {
            'name': 'Wheat Flour',
            'price': 55.00,
            'description': 'Pure wheat flour for rotis and breads.',
            'image': 'wheat flour.jpg',
            'stock': 90
        }
    ]
    
    for product_data in products:
        # Check if product already exists
        existing_product = Product.query.filter_by(name=product_data['name']).first()
        if not existing_product:
            product = Product(**product_data)
            db.session.add(product)
    
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    # Get all products from the database
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Product added to cart!')
    return redirect(url_for('home'))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    if request.method == 'POST':
        # Here you would typically integrate with a payment gateway
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return render_template('checkout.html', payment_success=True, cart_items=[], total=0)
    return render_template('checkout.html', cart_items=cart_items, total=total, payment_success=False)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        add_products()  # Add products when the app starts
    app.run(debug=True) 