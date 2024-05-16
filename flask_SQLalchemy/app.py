# these are the codes to make virtual envirnment and install this remain app to do this flask app
# the belwo codes are makes table for our mysql database and show all of them in our postman
'''
1:python3 -m venv myenv  
2:source myenv/bin/activate  
4:pip3 list     
Note: to install flask-SQL alchemy and SQL alchemy the below is the code 
1: pip install flask sqlalchemy flask-sqlalchemy flask-marshmallow mysql-connector-python
'''

from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://root:Ameerhamzaaziz@127.0.0.1/e-commerce-db"
db = SQLAlchemy(app)
ma = Marshmallow(app)

class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone", "id")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class Customer(db.Model):
    __tablename__ = "Customers"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship("Order", backref="Customer") # establishing our relationship

class Order(db.Model):
    __tablename__ = "Orders"
    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.Date,nullable=False)
    customer_id = db.Column(db.Integer,db.ForeignKey("Customers.id"))

# one to one
class CustomerAccount(db.Model):
    __tablename__ = "Customer_Accounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customers.id"))
    customer = db.relationship("Customer", backref="customer_account", uselist=False)

# many to many 
order_product = db.Table("Order_product",
        db.Column("order_id", db.Integer,db.ForeignKey("Orders.id"),primary_key=True),
        db.Column("product_id",db.Integer,db.ForeignKey("Products.id",primary_key=True))    
)

class Product(db.Model):
    __tablename__ = "Products"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    price = db.Column(db.Float,nullable=False)
    orders = db.relationship("order", secondary=order_product,backref=db.backref("products"))

#to get or to see all table info
@app.route("/customers", methods=["GET"])
def get_customers():
    customers =  Customer.query.all()
    return customers_schema.jsonify(customers)

@app.route("/customers", methods=["POST"])
def add_customer ():
    try:
        # Validate and deserialize input 
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    
    new_customer = Customer(name=customer_data["name"],email=customer_data["email"],phone=customer_data["phone"])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"}),201


@app.route("/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    
    customer.name = customer_data["name"]
    customer.email = customer_data["email"]
    customer.phone = customer_data["phone"]
    db.session.commit()
    return jsonify({"message": " customer details updated successfully"}),200

@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": " suctomer deleted successfully"}),200


# initialize the database and create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)


