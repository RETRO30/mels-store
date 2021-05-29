from flask import Flask
from flask import render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.users import User, Admin
from data.products import Product, Category
import re
import generator
import email_sender

port = 8080
host = '127.0.0.1'
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Yw4vYQMEHSDP8TeN9tBe'
login_manager = LoginManager()
login_manager.init_app(app)


def is_correct_password(password):
    if len(password) >= 8:
        return True
    else:
        return False


def is_correct_phone_number(number):
    if re.match(r'^(\+?79?|\+?77?|89?|87?|9|7)(\d{9})$', number):
        return True
    else:
        return False


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_page():
    db_sess = db_session.create_session()

    category = [[category.id, category.name] for category in db_sess.query(Category).all()]
    products = [
        [product.id,
         product.name,
         product.about,
         product.image_link,
         product.stock,
         product.cost,
         [product.category_id, [item[1] for item in category if item[0] == product.category_id][0]]] for product in
        db_sess.query(Product).all()]

    return render_template('main.html', title='Mels store - детское питание в Уфе', products=products, category=category)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/user')
    else:
        if request.method == 'POST':

            name = request.form.get('name')
            surname = request.form.get('surname')
            email = request.form.get('email')
            password = request.form.get('password')
            again_password = request.form.get('again_password')
            phone_number = request.form.get('phone_number')

            if not name or not surname or not email or not password or not phone_number:
                return render_template('register.html', title='Регистрация',
                                       message="Заполните все поля")

            if password != again_password:
                return render_template('register.html', title='Регистрация',
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == email).first():
                return render_template('register.html', title='Регистрация',
                                       message="Такой пользователь уже есть")

            if not is_correct_password(password):
                return render_template('register.html', title='Регистрация',
                                       message="Пароль слишком короткий")

            if not is_correct_phone_number(phone_number):
                return render_template('register.html', title='Регистрация',
                                       message="Неверный формат номера телефона")

            user = User(
                name=name,
                surname=surname,
                phone_number=phone_number,
                email=email,
                email_confirmed=generator.generate(6)
            )

            user.set_password(password)
            db_sess.add(user)
            db_sess.commit()

            email_sender.send_message(
                user.email,
                'Добро пожаловать в Mels-store',
                f'Код подтверждения: {user.email_confirmed}')

            return redirect('/login')
        return render_template('register.html', title='Регистрация')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == request.form.get('email')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user, remember=request.form.get('remember_me'))
            if user.email_confirmed == 'True':
                return redirect("/")
            else:
                return redirect("/confirm")
        return render_template('login.html',
                               message="Неправильный логин или пароль", title='Вход')
    return render_template('login.html', title='Вход')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/user', methods=['GET', 'POST'])
def user_page():
    if current_user.is_authenticated:
        if request.method == 'POST':
            if request.form['submit_button'] == 'save_info':

                name = request.form.get('name')
                surname = request.form.get('surname')
                phone_number = request.form.get('phone_number')

                if not name or not surname or not phone_number:
                    return render_template('user.html', title='Личный кабинет', message='Заполните все поля.')
                if not is_correct_phone_number(phone_number):
                    return render_template('user.html', title='Личный кабинет',
                                           message='Неверный формат номера телефона. Формат: +7XXXXXXXXXX')

                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.id == current_user.id).first()

                user.name = name
                user.surname = surname
                user.phone_number = phone_number

                db_sess.commit()

                return redirect('/')
            if request.form['submit_button'] == 'save_password':

                old_password = request.form.get('old_password')
                new_password = request.form.get('new_password')
                again_password = request.form.get('again_password')

                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.id == current_user.id).first()

                if not user.check_password(old_password):
                    return render_template('user.html', title='Личный кабинет', message='Неверный старый пароль.')
                if new_password != again_password:
                    return render_template('user.html', title='Личный кабинет', message='Новые пароли не совпадают.')
                if not is_correct_password(new_password):
                    return render_template('user.html', title='Личный кабинет',
                                           message='Новый пароль слишком короткий.')

                user.set_password(new_password)

                db_sess.commit()

                return redirect('/')
        return render_template('user.html', title='Личный кабинет')
    else:
        return redirect('/')


@app.route('/confirm', methods=['GET', 'POST'])
def confirm_page():
    if request.method == 'POST':
        if request.form.get('Code') == current_user.email_confirmed:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == current_user.id).first()
            user.email_confirmed = 'True'
            db_sess.commit()
            return redirect("/")
        else:
            return render_template('message_confirm_email.html', title='Вход', message='Код неверный')
    return render_template('message_confirm_email.html', title='Вход')


@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    db_sess = db_session.create_session()
    admin = db_sess.query(Admin).filter(Admin.user_id == current_user.id).first()

    if admin:

        if request.method == 'POST':
            if request.form['submit_button'] == 'add_admin_btn':
                try:
                    id_new_admin = request.form.get('add_admin').split()[2][:-1]
                    if not db_sess.query(Admin).filter(Admin.user_id == id_new_admin).first():
                        new_admin = Admin(user_id=id_new_admin)
                        db_sess.add(new_admin)
                        db_sess.commit()
                except Exception as e:
                    print(e)

            if request.form['submit_button'] == 'add_product':
                try:
                    name = request.form.get('add_name')
                    about = request.form.get('add_about')
                    image_link = request.form.get('add_image_link')
                    stock = request.form.get('add_stock')
                    cost = request.form.get('add_cost')
                    product_category = request.form.get('add_category')

                    new_product = Product(
                        name=name,
                        about=about,
                        image_link=image_link,
                        stock=stock,
                        cost=cost,
                        category_id=product_category
                    )

                    db_sess.add(new_product)
                    db_sess.commit()
                except Exception as e:
                    print(e)

            if request.form['submit_button'] == 'edit_product':
                try:
                    id = request.form.get('edit_id')
                    name = request.form.get('edit_name')
                    about = request.form.get('edit_about')
                    image_link = request.form.get('edit_image_link')
                    stock = request.form.get('edit_stock')
                    cost = request.form.get('edit_cost')
                    product_category = request.form.get('edit_category')

                    product = db_sess.query(Product).filter(Product.id == id).first()
                    product.name = name
                    product.about = about
                    product.image_link = image_link
                    product.stock = stock
                    product.cost = cost
                    product.category_id = product_category
                    db_sess.commit()

                except Exception as e:
                    print(e)
            if request.form['submit_button'] == 'delete_product':
                try:
                    id = request.form.get('delete_select')
                    if id:
                        product = db_sess.query(Product).filter(Product.id == id).first()
                        db_sess.delete(product)
                        db_sess.commit()
                except Exception as e:
                    print(e)

            if request.form['submit_button'] == 'add_category':
                try:
                    name = request.form.get('add_name_category')
                    new_category = Category(name=name)

                    db_sess.add(new_category)
                    db_sess.commit()
                except Exception as e:
                    print(e)
            if request.form['submit_button'] == 'edit_category':
                try:
                    id = request.form.get('edit_id_category')
                    name = request.form.get('edit_name_category')

                    edit_category = db_sess.query(Category).filter(Category.id == id).first()
                    edit_category.name = name
                    db_sess.commit()
                except Exception as e:
                    print(e)

            if request.form['submit_button'] == 'delete_category':
                try:
                    id = request.form.get('delete_select_category')
                    if id:
                        delete_category = db_sess.query(Category).filter(Category.id == id).first()
                        db_sess.delete(delete_category)
                        db_sess.commit()
                except Exception as e:
                    print(e)

        users = [[user.id, user.name, user.surname, user.email, user.phone_number] for user in
                 db_sess.query(User).all()]
        category = [[category.id, category.name] for category in db_sess.query(Category).all()]
        products = [
            [product.id,
             product.name,
             product.about,
             product.image_link,
             product.stock,
             product.cost,
             [product.category_id, [item[1] for item in category if item[0] == product.category_id][0]]] for product in
            db_sess.query(Product).all()]
        return render_template('admin_panel.html', title='Панель админитратора', users=users, products=products,
                               category=category)

    else:
        return 'Недостаточно прав'


@app.route('/product/<id>', methods=['GET', 'POST'])
def product_page(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    return render_template(
        'product.html',
        title=product.name,
        product_name=product.name,
        product_about=product.about,
        product_cost=product.cost,
        product_stock=product.stock,
        product_image=product.image_link,
        product_category=db_sess.query(Category).filter(Category.id == product.category_id).first().name
    )


if __name__ == '__main__':
    db_session.global_init("db/shop.db")
    app.run(port=port, host=host)
