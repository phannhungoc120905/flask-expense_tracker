from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from datetime import datetime
from models import db, Category, Transaction
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User
from sqlalchemy import func 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SECRET_KEY'] = 'a-random-string-that-you-can-not-guess'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to see this page'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('Username or Password not true!', 'danger')
            return redirect(url_for('login'))
        
        login_user(user)
        flash('Login successful!', "success")
        return redirect(url_for('home'))
    return render_template('login.html', title = 'Login')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            flash("Pass do not match!", 'warning')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first() is not None:
            flash('username has been used.', 'warning')
            return redirect(url_for('register'))
        
        new_user = User(username = username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
    return render_template('register.html', title = 'Register')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    query = Transaction.query.filter_by(author=current_user)

    # --- Lọc theo tháng ---
    selected_month_str = request.args.get('month','')
    if selected_month_str and len(selected_month_str) == 7:
        try:
            selected_month = datetime.strptime(selected_month_str, '%Y-%m').date()
            query = query.filter(
                db.extract('year', Transaction.date) == selected_month.year,
                db.extract('month', Transaction.date) == selected_month.month
            )
        except (ValueError, IndexError):
            flash("Định dạng tháng không hợp lệ.", "warning")

    # --- Lọc theo danh mục ---
    selected_category_id = request.args.get('category', '')
    if selected_category_id.isdigit():
        query = query.filter(Transaction.category_id == int(selected_category_id))

    # --- Thống kê ---
    total_amount = query.with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    average_amount = query.with_entities(db.func.avg(Transaction.amount)).scalar() or 0
    transaction_count = query.with_entities(db.func.count()).scalar() or 0

    budget = current_user.monthly_budget
    percent_spent = 0
    if budget and budget > 0:
        percent_spent = (total_amount / budget) * 100
        percent_spent = round(percent_spent, 2)

    # --- Phân trang ---
    page = request.args.get('page', 1, type=int)
    transactions = query.order_by(Transaction.date.desc()).paginate(page=page, per_page=5)

    categories = Category.query.all()

    return render_template('index.html',
                           transactions=transactions,
                           categories=categories,
                           total=total_amount,
                           average=average_amount,
                           count=transaction_count,
                           selected_month=selected_month_str,
                           selected_category_id=selected_category_id,
                           budget=budget,
                           percent_spent=percent_spent,)

@app.route('/api/chart-data')
@login_required
def chart_data():
    try:
        query = db.session.query(
            Category.name,
            func.sum(Transaction.amount).label('total_amount')
        ).join(Transaction).filter(
            Transaction.author == current_user
        ).group_by(Category.name)

        selected_month_str = request.args.get('month','')
        if selected_month_str and len(selected_month_str) == 7:
            try:
                year_str, month_str = selected_month_str.split('-')
                year, month = int(year_str), int(month_str)
                query = query.filter(
                    db.extract('year', Transaction.date) == year,
                    db.extract('month', Transaction.date) == month
                )
            except (ValueError, IndexError):
                pass
        
        selected_category_id = request.args.get('category','')
        if selected_category_id.isdigit():
            query = query.filter(Category.id == int(selected_category_id))

        category_data = query.order_by(Category.name).all()
        labels = [row[0] for row in category_data]
        data = [float(row[1]) for row in category_data]

        return jsonify({'labels': labels, 'data': data})
    except Exception as e:
        print(f"Error in /api/chart-data: {e}")
        return jsonify({'labels': [], 'data': [], 'error': str(e)}), 500

@app.route('/add', methods=['POST'])
@login_required
def add_transaction():
    try:
        description = request.form['description'].strip()
        amount = float(request.form['amount'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        category_id = int(request.form['category_id'])

        if not description or amount <= 0:
            flash('Vui lòng nhập mô tả và số tiền hợp lệ.', 'warning')
            return redirect(url_for('home'))

        new_transaction = Transaction(description=description,
                                      amount=amount,
                                      date=date,
                                      category_id=category_id,
                                      author=current_user)
        db.session.add(new_transaction)
        db.session.commit()
        flash('Đã thêm chi tiêu thành công!', 'success')

    except ValueError:
        flash('Dữ liệu không hợp lệ.', 'danger')

    return redirect(url_for('home'))

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Đã xóa chi tiêu.', 'success')
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.author != current_user:
        flash("You cant access this action!",'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        
        description = request.form.get('description', '').strip()
        amount_str = request.form.get('amount', '')
        date_str = request.form.get('date', '')
        category_id_str = request.form.get('category_id', '')

             # 3. Kiểm tra dữ liệu đầu vào (Validation) một cách chặt chẽ
        errors = []
        if not description:
            errors.append('Mô tả không được để trống.')
        if not date_str:
            errors.append('Ngày không được để trống.')
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                errors.append('Số tiền phải là một số dương.')
        except (ValueError, TypeError):
            errors.append('Số tiền không hợp lệ.')
            # Nếu có bất kỳ lỗi nào, flash tất cả lỗi và hiển thị lại form
        if errors:
            for error in errors:
                flash(error, 'danger')
            # Phải truyền lại categories khi render lại template
            categories = Category.query.all()
            return render_template('edit.html', transaction=transaction, categories=categories)
        # 4. Nếu không có lỗi, cập nhật vào database
        transaction.description = description
        transaction.amount = amount
        transaction.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        transaction.category_id = int(category_id_str)
        
        db.session.commit()
        flash('Giao dịch đã được cập nhật thành công!', 'success')
        return redirect(url_for('home'))
    
    all_categories = Category.query.all()

    return render_template('edit.html', transaction=transaction, categories=all_categories)

@app.route('/api/add_category', methods=['POST'])
@login_required
def api_add_category():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'status': 'error', 'message':'Category name is required'}), 400
    
    new_name = data['name'].strip()
    if not new_name:
        return jsonify({'status' : 'error','message': 'Category name cannot be blank'}), 400
    
    new_category = Category(name=new_name, author=current_user)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message' : 'Category added successfully!',
        'category':{
            'id': new_category.id,
            'name': new_category.name
        }
    }), 201
@app.route('/categories')
@login_required
def manage_categories():
    return "This is the page to manage categories."

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            new_budget_str = request.form.get('budget', '0').strip()
            new_budget = float(new_budget_str)

            if new_budget < 0:
                flash('The budget cannot be negative!','danger')
            else:
                current_user.monthly_budget = new_budget
                db.session.commit()
                flash('Budget updated successfully!', 'success')
            
            return redirect(url_for('profile'))
        except ValueError:
            flash('Please enter a valid number for the budget.', 'danger')
            return redirect(url_for('profile'))
    
    return render_template('profile.html', title='My Profile')
@app.cli.command('seed-db')
def seed_db():
    sample_categories = ['Ăn uống', 'Giải trí', 'Học tập', 'Đi lại', 'Mua sắm']
    for name in sample_categories:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    db.session.commit()
    print('Đã thêm dữ liệu mẫu vào bảng Category.')

if __name__ == '__main__':
    app.run(debug=True)
