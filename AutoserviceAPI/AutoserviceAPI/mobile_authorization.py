from AutoserviceAPI import app, db, allowed_file, login_manager, start_verification, check_verification, user_datastore
from flask import Flask, url_for, redirect, render_template, request, abort, jsonify
from AutoserviceAPI.model import User, Role, City, Category
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/signin', methods=['POST'])
def signin():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify(msg = 'Please check your login details and try again.'), 401

    if not check_password_hash(user.password, password):
        return jsonify(msg = 'Please check your password details and try again.'), 401

    login_user(user)
    token = create_access_token(identity = user.email)


    return jsonify(user.serialize(token)), 200

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    phone = request.form.get('phone')
    avatar = request.form.get('avatar')
    about = request.form.get('about')
    category_id = request.form.get('category_id')
    city_id = request.form.get('city_id')
    roles = request.form.get('roles')

    user = User.query.filter_by(email=email).first()
    
    if user:
        return jsonify(msg = 'Email address already exists.'), 400

    user = User.query.filter_by(phone=phone).first()
    if user:
        return jsonify(msg = 'Phone adress already exists.'), 400

    if avatar == "":
        avatar = 'noavatar.jpg'

    user_role = Role(name='customer')
    cid = []
    caid = []
    if roles == 1:
        user_role = Role (name='executor') 
        cid = [City.query.filter_by(id = city_id).first()]
        caid = [City.query.filter_by(id = category_id).first()]

    new_user = user_datastore.create_user(
        email=email, 
        name=name, 
        password=generate_password_hash(password, method='sha256'), 
        phone=phone, 
        avatar=avatar, 
        about=about, 
        category_id = caid, 
        city_id = cid, 
        roles=[user_role]
    )

    print("Phone : %s", phone)
    
    start_verification(phone)
    session['phone'] = phone

    db.session.add(new_user)
    db.session.commit()

    return jsonify(msg ="User Created"),200

@app.route('/load_file', methods=["PUT"])
def load_file():
    for file in request.files:
        if file and allowed_file(file.filename) and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/uploads/<filename>', methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/verify', methods=["POST"])
def verify():
    phone = session.get('phone')
    code = request.form['code']
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(msg = 'Please check your login details and try again.'), 401

    if check_verification(phone, code):
        user.is_vetified = True;
        db.session.commit()
        return jsonify (msg = "Verified"), 200
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
