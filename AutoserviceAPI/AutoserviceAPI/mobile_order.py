from AutoserviceAPI import app, db, allowed_file, login_manager, start_verification, check_verification, user_datastore, jwt
from flask import Flask, url_for, redirect, render_template, request, abort, jsonify
from AutoserviceAPI.model import User, Role, City, Category, Order, Recalls
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/create_order', methods=['POST'])
@jwt_required()
def create_order():
    description = request.form.get('description')
    category_id = request.form.get('category_id')
    city_id = request.form.get('city_id')
    user_id = request.form.get('user_id')
    date = request.form.get('date')
    price = request.form.get('price')
    #images = request.form.get('images')

    order = Order (description = description, category_id = category_id, city_id = city_id, user_id = user_id, date = date, price = price)

    db.session.add(order)
    db.session.commit()

    return jsonify (msg = "Order Created"), 200

@app.route('/get_orders', methods=['POST'])
@jwt_required()
def get_orders():
    phone = get_jwt_identity()
    user = User.query.filter_by(phone=phone).first()

    orders = Order.quety.filter_by(user_id=user.id)

    return jsonfy(orders = [i.serialize for i in orders]), 200

@app.route('/get_executor_orders', methods=['POST'])
@jwt_required()
def get_executor_orders():
    phone = get_jwt_identity()
    user = User.query.filter_by(phone=phone).first()

    orders = Order.quety.filter_by(category_id=user.category_id)

    return jsonfy(orders = [i.serialize for i in orders]), 200

@app.route('/create_recall', methods=['POST'])
@jwt_required()
def create_recall():
    description = request.form.get('description')
    user_id = request.form.get('user_id')
    date = request.form.get('date')
    price = request.form.get('price')
    time = request.form.get('time')
    order_id = request.form.get('order_id')

    recall = Recalls(description=description, user_id=user_id, date=date, price=price, time=time, order_id=order_id)

    db.session.add(recall)
    db.session.commit()

    return jsonify (msg = "Recall Created"), 200

@app.route('/get_recalls', methods=['POST'])
@jwt_required()
def get_recalls():
    order_id = request.form.get('order_id')
    recalls = Recalls.query.filtered_by(order_id=order_id)

    return jsonfy(recalls = [i.serialize for i in recalls]), 200