from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, expose
from wtforms import PasswordField
from AutoserviceAPI import db
import datetime


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

users_category = db.Table(
    'users_category',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('category_id', db.Integer(), db.ForeignKey('category.id'))
)

users_city = db.Table(
    'users_city',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('city_id', db.Integer(), db.ForeignKey('city.id'))
)

order_images = db.Table(
    'order_images',
    db.Column('order_id', db.Integer(), db.ForeignKey('order.id')),
    db.Column('images_id', db.Integer(), db.ForeignKey('images.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    deviceid = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    phone = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))
    about = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default = True)
    banned = db.Column(db.Boolean(), default = False)
    is_verified = db.Column(db.Boolean(), default = False)
    plan_date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    confirmed_at = db.Column(db.DateTime())
    tokken = db.Column(db.String(255))
    role = db.Column(db.Integer)

    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    order = db.relationship('Order', backref='user', lazy=True)
    recalls = db.relationship('Recalls', backref='user', lazy=True)

    def __str__(self):
        return self.phone

    @property
    def serialize (self):
        return {
                "id" : self.id,
                "name" : self.name,
                "email" : self.email,
                "phone" : self.phone,
                "avatar" : self.avatar,
                "about" : self.about,
                "category_id" : self.category_id,
                "city_id" : self.city_id,
                "plan_date" : str(self.plan_date),
                "roles" : self.role,
                "token" : self.tokken
            }



class City (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    order = db.relationship('Order', backref='city', lazy=True)
    user = db.relationship('User', backref='city', lazy=True)

    def __str__(self):
        return self.name

    @property
    def serialize (self):
        return {
                "id" : self.id,
                "name" : self.name
            }


class Category(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    price = db.Column(db.String(255))
    parent_id = db.Column(db.Integer())
    showUserdata = db.Column(db.Boolean(), default = False)

    order = db.relationship('Order', backref='category', lazy=True)
    user = db.relationship('User', backref='category', lazy=True)

    def __str__(self):
        return self.name

    @property
    def serialize (self):
        return {
                "id" : self.id,
                "name" : self.name,
                "description" : self.description,
                "parent_id" : self.parent_id,
                "price" : self.price,
                "showUserdata" : self.showUserdata
            }

class Order(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime())
    price = db.Column(db.String(255))

    recalls = db.relationship('Recalls', backref='order', lazy=True)
    images = db.relationship('Images', secondary=order_images,
                            backref=db.backref('order', lazy='dynamic'))

    @property
    def serialize (self):
        return {
                "id" : self.id,
                "description" : self.description,
                "category_id" : self.category_id,
                "city_id" : self.city_id,
                "user_id" : self.user_id,
                "date" : self.date,
                "images" : self.images,
                "price" :  self.price
            }

class Images(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.String(255))

    def __str__(self):
        return self.url

class Recalls(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime())
    price = db.Column(db.String(255))
    time = db.Column(db.String(255))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

    @property
    def serialize (self):
        return {
                "id" : self.id,
                "description" : self.description,
                "user_id" : self.user_id,
                "date" : self.date,
                "price" : self.price,
                "time" : self.time,
                "order_id" : self.order_id
            }


class Feetback(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    customer_id = db.Column(db.Integer())
    reyting = db.Column(db.Integer())
    message = db.Column(db.String(255))

    @property
    def serialize (self):
        return {
                "id" : self.id,
                "user_id" : self.user_id,
                "customer_id" : self.customer_id,
                "reyting" : self.reyting,
                "message" : self.message
            }

class Chats(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer())
    customer_id = db.Column(db.Integer())

    @property
    def serialize (self):
        return {
                "id" : self.id,
                "user_id" : self.user_id,
                "customer_id" : self.customer_id
            }