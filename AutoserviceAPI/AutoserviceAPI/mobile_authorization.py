from AutoserviceAPI import app, db, allowed_file, login_manager, start_verification, check_verification
from flask import Flask, url_for, redirect, render_template, request, abort
from AutoserviceAPI.model import User
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


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
    
    about = request.form.get('about')
    category_id = request.form.get('category_id')
    city_id = request.form.get('city_id')
    roles = request.form.get('roles')

    user = User.query.filter_by(email=email).first()
    
    if user:
        return jsonify(msg = 'Email address already exists.'), 400

    avatar = 'noavatar.jpg'

    if 'file' in request.files:
        file = request.files['file']

        if file and allowed_file(file.filename) and file.filename != '':
            filename = secure_filename(file.filename)
            avatar = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), phone=phone, avatar=avatar, about=about, category_id = category_id, city_id = city_id, roles=roles)

    
    vsid = start_verification(phone)
    session['phone'] = phone

    db.session.add(new_user)
    db.session.commit()

    return jsonify(msg ="User Created"),200

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/verify', methods=["POST"])
def verify():
    email = session.get('email')
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
    email = session.get('email')
    phone = session.get('phone')
    code = request.form['code']

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(msg = 'Please check your login details and try again.'), 401
    
    vsid = start_verification(phone)
    session['phone'] = phone
    return jsonify(msg = "code sended"), 200

@app.route("/reset_password", methods=["POST"])
def reset_password():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    
    if user:
        return jsonify(msg = 'Email address already exists.'), 400

    user.password = generate_password_hash(password, method='sha256')

    db.session.commit()
    return jsonify(msg = 'Password Reseted'),200
