
#! /var/www/adamovproject.pp.ua/web/virtenv/bin python
# -*- coding: utf-8 -*-

from AutoserviceAPI import app, db, allowed_file, login_manager, start_verification, check_verification, user_datastore
from flask import Flask, url_for, redirect, render_template, request, abort, jsonify, session
from AutoserviceAPI.model import User, Role, City, Category, Images
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import io
from PIL import Image

@app.route('/signin', methods=['POST'])
def signin():
    phone = request.form.get('phone')
    session['phone'] = phone;
    session["deviceid"] = request.form.get('deviceid')
    start_verification(phone)
    
    return jsonify(msg = 'Mesaage Sended.'), 200

@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone')
    deviceid = request.form.get('deviceid')

    user = User.query.filter_by(phone=phone).first()

    if user.deviceid != deviceid:
        return jsonify(msg = "Device unverifaed"), 200

    login_user(user)
    token = create_access_token(identity = user.phone)
    
    return jsonify(user.serialize(token)),200

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    avatar = request.form.get('avatar')
    about = request.form.get('about')
    category_id = request.form.get('category_id')
    city_id = request.form.get('city_id')
    roles = request.form.get('roles')
    images = request.form.get('images')
    plan_date = request.form.get('plan_date')


    user = User.query.filter_by(phone=phone).first()

    if not user:
        if avatar == "":
            avatar = 'noavatar.jpg'
        images = Images(url = avatar)
        db.session.add(images)

        user = user_datastore.create_user(
            phone=phone, 
            name = name, 
            email = email, 
            about = about,
            avatar = avatar,
            category_id = category_id, 
            city_id = city_id, 
            deviceid = session["deviceid"],
            role = roles
        )
    db.session.commit()
    login_user(user)
    user.tokken = str(create_access_token(identity = phone))

    return jsonify(user.serialize),200

@app.route('/user_update', methods=['POST'])
@jwt_required()
def user_update():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    avatar = request.form.get('avatar')
    about = request.form.get('about')
    category_id = request.form.get('category_id')
    city_id = request.form.get('city_id')
    roles = request.form.get('roles')

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify(msg = "User not Exist"), 400

    user_role = Role(name='customer')
    cid = []
    caid = []
    if roles == 1:
        user_role = Role (name='executor') 
        cid = [City.query.filter_by(id = city_id).first()]
        caid = [City.query.filter_by(id = category_id).first()]

    user.name = name
    user.email = email
    user.phone = phone
    user.avatar = avatar
    user.about = about
    user.category_id = cid
    user.city_id = cid
    user.roles = [user_role]
    user.deviceid = session["deviceid"]

    return jsonify(msg = "User updated"), 200

@app.route('/load_file', methods=["PUT"])
def load_file():
    name = request.form.get('name')
    file = Image.open(io.BytesIO(request.get_data()))
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], name))
    return jsonify(msg = "Loaded"),200


@app.route('/uploads/<filename>', methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/verify', methods=["POST"])
def verify():
    phone = session.get('phone')
    code = request.form['code']
    deviceid = request.form.get('deviceid')

    if session["deviceid"] != request.form.get('deviceid'):
        return jsonify(msg = "Устройсво не Верефецированно"), 401

    user = User.query.filter_by(phone=phone).first()
    if user:
        user.deviceid = deviceid
        db.session.commit()

    if check_verification(phone, code):
        return jsonify (msg = "Verified"), 200
    else:
        return jsonify (msg = "Verification Error"), 400

@app.route('/resend', methods=["POST"])
def resend():
    phone = session.get('phone')

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify(msg = 'Please check your login details and try again.'), 401
    
    vsid = start_verification(phone)
    session['phone'] = phone
    return jsonify(msg = "code sended"), 200

@app.route("/reset_password", methods=["POST"])
def reset_password():
    phone = request.form.get('phone')
    password = request.form.get('password')

    user = User.query.filter_by(phone=phone).first()
    
    if not user:
        return jsonify(msg = 'Now User with this phone number'), 400

    user.password = generate_password_hash(password, method='sha256')

    db.session.commit()
    return jsonify(msg = 'Password Reseted'),200
