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


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

users_city = db.Table(
    'users_city',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('city_id', db.Integer(), db.ForeignKey('city.id'))
)

users_category = db.Table(
    'users_category',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('category_id', db.Integer(), db.ForeignKey('category.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255))
    avatar = db.Column(db.String(255))
    about = db.Column(db.String(255))
    category_id = db.relationship('Category', secondary=users_category,
                            backref=db.backref('users', lazy='dynamic'))
    city_id = db.relationship('City', secondary=users_city,
                            backref=db.backref('users', lazy='dynamic'))
    active = db.Column(db.Boolean(), default = True)
    banned = db.Column(db.Boolean(), default = False)
    is_verified = db.Column(db.Boolean(), default = False)
    plan_date = db.Column(db.DateTime())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

    @property
    def serialize (self, token):
        return {
                'id' : seld.id,
                'name' : self.name,
                'email' : self.email,
                'phone' : self.phone,
                'avatar' : self.avatar,
                'about' : self.about,
                'category_id' : self.category_id[0],
                'city_id' : self.city_id[0],
                'plan_date' : plan_date,
                'roles' : self.roles[0],
                'token' : token
            }



class City (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

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
    parent_id = db.Column(db.Integer())

    def __str__(self):
        return self.name

    @property
    def serialize (self):
        return {
                "id" : self.id,
                "name" : self.name,
                "description" : self.description,
                "parent_id" : self.parent_id
            }
