from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import app
from models import db, Ad, User  
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename 
from PIL import Image
from io import BytesIO
from jinja2 import Environment

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d.%m.%Y %H:%M'):
    return value.strftime(format)

@app.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    
    query = Ad.query.join(User).order_by(Ad.created_at.desc())
    
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Ad.title.ilike(search),
                Ad.content.ilike(search),
                User.username.ilike(search)
            )
        )
    
    ads = query.all()
    return render_template('index.html', ads=ads)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_ad():
    if request.method == 'POST':
        try:
            image_file = request.files.get('image')
            filename = None
            
            if image_file and image_file.filename != '':
                filename = current_user.generate_filename(image_file.filename)
                user_upload_dir = os.path.join(
                    app.config['UPLOAD_FOLDER'], 
                    f"user_{current_user.id}"
                )

                if not os.path.exists(user_upload_dir):
                    os.makedirs(user_upload_dir)

                image_path = os.path.join(user_upload_dir, filename)
                image_file.save(image_path)

                img = Image.open(image_path)
                img.thumbnail((200, 200))
                thumbnail_path = os.path.join(user_upload_dir, f"thumb_{filename}")
                img.save(thumbnail_path)
                
                filename = f"user_{current_user.id}/thumb_{filename}"

            ad = Ad(
                title=request.form['title'],
                content=request.form['content'],
                image=filename,
                user_id=current_user.id
            )
            
            db.session.add(ad)
            db.session.commit()
            flash('Объявление добавлено!', 'success')
        
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'error')
        
        return redirect(url_for('index'))
    
    return render_template('add.html')

@app.route('/ad/<int:id>')
def view_ad(id):
    ad = Ad.query.get_or_404(id)
    return render_template('ad.html', ad=ad)

@app.route('/delete/<int:id>')
@login_required
def delete_ad(id):
    ad = Ad.query.get(id)

    if ad.user_id != current_user.id:
        flash('Недостаточно прав для удаления', 'error')
        return redirect(url_for('index'))
        
    try:
        db.session.delete(ad)
        db.session.commit()
        flash('Объявление удалено', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'error')
    
    return redirect(url_for('index'))  

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Имя пользователя уже занято', 'error')
            return redirect(url_for('register'))
            
        user = User(
            username=form.username.data,
            phone=form.phone.data,
            password=generate_password_hash(form.password.data)
        )
        
        db.session.add(user)
        try:
            db.session.commit()
            login_user(user)
            flash('Регистрация успешна!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'error')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if not user or not check_password_hash(user.password, form.password.data):
            flash('Неверный логин или пароль', 'error')
            return redirect(url_for('login'))
            
        login_user(user)
        flash('Успешный вход!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)