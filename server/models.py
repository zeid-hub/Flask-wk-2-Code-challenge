from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

restaurant_pizza_association = db.Table(
    'restaurant_pizza',
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurants.id'), primary_key=True),
    db.Column('pizza_id', db.Integer, db.ForeignKey('pizzas.id'), primary_key=True)
)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    pizzas = db.relationship('Pizza', secondary=restaurant_pizza_association, backref='restaurants_associated')

    # add serialization rules
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        return f'<Restaurant {self.name}>'


class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurants = db.relationship('Restaurant', secondary=restaurant_pizza_association, backref='pizzas_associated')

    # add serialization rules
    serialize_rules = ('-restaurant_pizzas.pizza',)

    def __repr__(self):
        return f'<Pizza {self.name}, {self.ingredients}>'


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    pizza_id = db.Column(db.Integer(), db.ForeignKey("pizzas.id"))
    restaurant_id = db.Column(db.Integer(), db.ForeignKey("restaurants.id"))

    # add relationships
    restaurant = db.relationship('Restaurant', backref=db.backref('restaurant_pizzas', cascade='all, delete-orphan'))
    pizza = db.relationship('Pizza', backref=db.backref('restaurant_pizzas', cascade='all, delete-orphan'))

    # add serialization rules
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas',)

    # add validation
    @validates('price')
    def validate_price(self, key, price):
        if price < 1 or price > 30:
            raise ValueError("Price must be between 1 and 30.")
        elif price == 0:
            raise ValueError("Price cannot be 0.")
        else:
            return price

    def __repr__(self):
        return f'<RestaurantPizza ${self.price}>'
