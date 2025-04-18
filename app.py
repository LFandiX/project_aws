from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, get_flashed_messages
from database import SQL
from datetime import date, datetime, timedelta


app = Flask(__name__)
app.secret_key = "your_secret_key"
db = SQL()

adminsD = {}
membersD = {}
adminL = []
memberL = []
cars_modelD = {}
carsD = {}
rentalsD = {}


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')  
        users = db.get_all_users()

        adminsD = {}
        membersD = {}
        for user in users:
            # {'ID_user': 1, 'name_user': 'Budi Santoso', 'email_user': 'budi@gmail.com', 'password_user': 'budi123', 'username_user': 'budi_s', 'role_user': 'member'}
            user_role = user['role_user']
            if user_role == "admin":
                adminsD[user['ID_user']] = [user['name_user'], user['username_user'], user['password_user'], user['email_user']]
                adminL.append(user['username_user'])
            elif user_role == "member":
                membersD[user['ID_user']] = [user['name_user'], user['username_user'], user['password_user'], user['email_user']]
                memberL.append(user['username_user'])

        dataD = {}
        if role.strip() == "admin":
            dataD = adminsD
        else:
            dataD = membersD    

        print(dataD)
        print(username, password)

        for id_user, datas in dataD.items():
            if datas[1] == username and datas[2] == password:
                session['username'] = username
                session['role'] = role
                session['user_id'] = id_user

                flash("Login successful!", "success")
                redirect_url = url_for('admin_homepage') if role == 'admin' else url_for('user_homepage')

                return jsonify({
                    "success": True,
                    "message": "Login successful!",
                    "flashes": get_flashed_messages(),
                    "redirect": redirect_url  
                }), 200
                  
        print("login success")
        return jsonify({
            "success": False,
            "message": "Invalid username or password!"
        }), 400
    
    return render_template("login_page.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Endpoint untuk registrasi user (GET untuk pengecekan username, POST untuk registrasi)
    """
    
    if request.method == 'POST':
        # Ambil data dari form
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # Validasi input tidak boleh kosong
        if not fullname or not email or not username or not password:
            return jsonify({"success": False, "message": "All fields are required"}), 400

        # Cek apakah username sudah digunakan
        if db.is_username_taken(username):
            print("username sudah ada")
            flash("Username is already used", "error")
            return render_template('register.html', error="Username is already used", form_data=request.form)

        # Cek apakah email sudah digunakan
        if db.is_email_taken(email):
            print("email sudah ada")
            flash("Email is already registered", "error")
            return render_template('register.html', error="Email is already registered", form_data=request.form)

        # Jika validasi lolos, buat akun baru
        db.create_user(fullname, email, password, username)
        flash("Registration successful! Please log in.", "success")
    
        return jsonify({
            "success": True,
            "message": "Registration successful! Redirecting to login.",
            "flashes": get_flashed_messages()
        }), 200

    return render_template('register.html')


@app.route('/check_username', methods=['POST'])
def check_username():
    username = request.json.get("username")
    
    if db.is_username_taken(username):
        return jsonify({"success": False, "message": "Username is already taken"}), 400
    return jsonify({"success": True, "message": "Username is available"}), 200


@app.route('/check_email', methods=['POST'])
def check_email():
    email = request.json.get("email")
    
    if db.is_email_taken(email):
        return jsonify({"success": False, "message": "Email is already registered"}), 400
    return jsonify({"success": True, "message": "Email is available"}), 200


@app.route('/check_username_login', methods=['POST'])
def check_username_login():
    username = request.json.get("username")
    
    if db.is_username_taken(username):
        print("terdaftar")
        return jsonify({"success": True, "message": "Username is registered."}), 400
    print("tidak terdaftar")
    return jsonify({"success": False, "message": "Username is not registered."}), 200


@app.route('/user_homepage', methods=['GET', 'POST'])
def user_homepage():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    id_user = session['user_id']

    cars = db.get_all_cars()
    rentals = db.get_all_rentals()

    available_cars = {}
    user_rentals = []
    
    for car in cars:
        car_id = car['ID_car']
        model_id = car['model_id']
        
        car_model = next((m for m in cars_model if m['ID_model'] == model_id), None)
        
        if car_model:
            available_cars[car_id] = {
                'license_plate': car['license_plate'],
                'availability': car['availability'],
                'brand': car_model['brand_car'],
                'model': car_model['model_car'],
                'year': car_model['year_manufactured'],
                'price': str(car_model['price_car']),  # Convert Decimal to string
                'image': car_model['image_car']
            }

    for rental in rentals:
        if rental['user_id'] == id_user:
            car_id = rental['car_id']
            car = next((c for c in cars if c['ID_car'] == car_id), None)
            
            if car:
                model_id = car['model_id']
                car_model = next((m for m in cars_model if m['ID_model'] == model_id), None)
                
                if car_model:
                    rental_info = {
                        'rental_id': rental['ID_rental'],
                        'rental_date': rental['rental_date'],
                        'return_date': rental['return_date'],
                        'approval_status': rental['approval_status'],
                        'car_info': {
                            'license_plate': car['license_plate'],
                            'availability': car['availability'],
                            'brand': car_model['brand_car'],
                            'model': car_model['model_car'],
                            'year': car_model['year_manufactured'],
                            'price': str(car_model['price_car']),  # Convert Decimal to string
                            'image': car_model['image_car']
                        }
                    }
                    
                    user_rentals.append(rental_info)

    return render_template('user_homepage.html', cars=available_cars, rentals=user_rentals)


@app.route('/add_rental', methods=['POST'])
def add_rental():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    data = request.get_json()
    car_brand = data.get('car_brand')
    price = data.get('price')

    cars_model = db.get_all_car_models()
    
    try:
        # Dapatkan ID mobil berdasarkan brand
        car_model = next((m for m in cars_model if m['brand_car'] == car_brand), None)
        if not car_model:
            return jsonify({'success': False, 'error': 'Car not found'}), 404

        available_car = next((c for c in db.get_all_cars() 
                            if c['model_id'] == car_model['ID_model'] 
                            and c['availability'] == 'available'), None)
        
        if not available_car:
            return jsonify({'success': False, 'error': 'No available car'}), 400

        # Tambahkan rental ke database
        rental_id = db.create_rental(
            user_id=session['user_id'],
            car_id=available_car['ID_car'],
            rental_date=datetime.now().date(),
            return_date=datetime.now().date() + timedelta(days=4),
            approval_status='pending'
        )

        return jsonify({
            'success': True,
            'rental_id': rental_id,
            'message': 'Rental request submitted'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/cancel_rental', methods=['POST'])
def cancel_rental():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    cars = db.get_all_cars()
    cars_model = db.get_all_car_models()
    amount_car_available = []
    models = {}

    data = request.get_json()
    car_brand = data.get('car_brand')

    for car in cars:
        if car['availability'] == "available":
            amount_car_available.append(car['ID_car'])

    for model in cars_model:
        models[model['brand_car']] = model['ID_model']

    try:

        car_id_target = ""
        for brand, id_ in models.items():
            if car_brand == brand:
                car_id_target = id_

        print(f"{car_id_target}")

        recent_rent_result = db.get_recent_rent(len(amount_car_available))
        for rent in recent_rent_result:
            if rent['car_id'] == car_id_target:
                id_rental_target = rent['ID_rental']
                db.delete_rental(id_rental_target)
                break

        return jsonify({
            'success': True,
            'car_brand': car_brand,
            'message': 'Rental cancelled successfully'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/process_payment', methods=['POST'])
def process_payment():
    data = request.get_json()
    rental_id = data.get('rental_id')
    total = data.get('total')
    
    if total is None or total <= 0:
        return jsonify({"success": False, "error": "Invalid total amount"}), 400

    # Simulate payment processing
    payment_success = True  

    if payment_success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Payment failed"})

@app.route('/admin_homepage', methods=['GET', 'POST'])
def admin_homepage():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    rentals = db.get_all_rentals()
    car_models = db.get_all_car_models()
    cars = db.get_all_cars()
    users = db.get_all_users() 
    
    rental_data = []

    for rental in rentals:
        car = next((c for c in cars if c['ID_car'] == rental['car_id']), None)
        car_model = next((m for m in car_models if m['ID_model'] == car['model_id']), None) if car else None
        user = next((u for u in users if u['ID_user'] == rental['user_id']), None)

        rental_info = {
            'rental_id': rental['ID_rental'],
            'rental_date': rental['rental_date'].strftime("%d/%m/%Y"),
            'return_date': rental['return_date'].strftime("%d/%m/%Y"),
            'approval_status': rental['approval_status'],
            'user_info': {
                'name': user['name_user'] if user else 'Unknown',
                'email': user['email_user'] if user else 'Unknown'
            },
            'car_info': {
                'license_plate': car['license_plate'] if car else 'Unknown',
                'brand': car_model['brand_car'] if car_model else 'Unknown',
                'model': car_model['model_car'] if car_model else 'Unknown',
                'year': car_model['year_manufactured'] if car_model else 'Unknown',
                'price': str(car_model['price_car']) if car_model else 'Unknown',
                'availability': car['availability'] if car else 'Unknown'
            }
        }
        
        rental_data.append(rental_info)

    return render_template('admin_homepage.html', rentals=rental_data)


@app.route('/rent_car', methods=['POST'])
def rent_car():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    car_id = request.form.get('car_id')
    rental_date = request.form.get('rental_date')
    return_date = request.form.get('return_date')
    
    if not car_id or not rental_date or not return_date:
        flash("All fields are required", "error")
        return redirect(url_for('user_homepage'))
    
    db.create_rental(session['user_id'], car_id, rental_date, return_date)
    flash("Car rental request submitted! Waiting for approval.", "success")
    return redirect(url_for('user_homepage'))


@app.route('/update_rental_status', methods=['GET', 'POST'])
def update_rental_status():
    data = request.json
    rental_id = data.get('rental_id')
    new_status = data.get('new_status')
    task = data.get('task')

    if not rental_id or not new_status:
        return jsonify({"success": False, "message": "Data tidak lengkap"}), 400

    try: # akses ke database SQL
        if new_status == "approved" and task == "approve":
            db.update_status_rental(rental_id, "approved")
        elif new_status == "rejected" and task == "reject":
            db.update_status_rental(rental_id, "rejected")   

        rental_data = []
        rentals = db.get_all_rentals()
        car_models = db.get_all_car_models()
        cars = db.get_all_cars()
        users = db.get_all_users() 

        for rental in rentals:
            car = next((c for c in cars if c['ID_car'] == rental['car_id']), None)
            car_model = next((m for m in car_models if m['ID_model'] == car['model_id']), None) if car else None
            user = next((u for u in users if u['ID_user'] == rental['user_id']), None)

            rental_info = {
                'rental_id': rental['ID_rental'],
                'rental_date': rental['rental_date'].strftime("%d/%m/%Y"),
                'return_date': rental['return_date'].strftime("%d/%m/%Y"),
                'approval_status': rental['approval_status'],
                'user_info': {
                    'name': user['name_user'] if user else 'Unknown',
                    'email': user['email_user'] if user else 'Unknown'
                },
                'car_info': {
                    'license_plate': car['license_plate'] if car else 'Unknown',
                    'brand': car_model['brand_car'] if car_model else 'Unknown',
                    'model': car_model['model_car'] if car_model else 'Unknown',
                    'year': car_model['year_manufactured'] if car_model else 'Unknown',
                    'price': str(car_model['price_car']) if car_model else 'Unknown',
                    'availability': car['availability'] if car else 'Unknown'
                }
            }
            
            rental_data.append(rental_info)

        print("data telah terkirim")
        return jsonify({
            "success": True, 
            "message": "Status rental diperbarui",
            "rental_data": rental_data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    if db.connection:
        users = db.get_all_users()
        cars = db.get_all_cars()
        cars_model = db.get_all_car_models()
        rentals = db.get_all_rentals()
        

        for user in users:
            # {'ID_user': 1, 'name_user': 'Budi Santoso', 'email_user': 'budi@gmail.com', 'password_user': 'budi123', 'username_user': 'budi_s', 'role_user': 'member'}
            role = user['role_user']
            if role == "admin":
                adminsD[user['ID_user']] = [user['name_user'], user['username_user'], user['password_user'], user['email_user']]
                adminL.append(user['username_user'])
            elif role == "member":
                membersD[user['ID_user']] = [user['name_user'], user['username_user'], user['password_user'], user['email_user']]
                memberL.append(user['username_user'])

        for c_model in cars_model:
            # {'ID_model': 1, 'brand_car': 'Toyota', 'year_manufactured': 2020, 'model_car': 'Avanza', 'price_car': Decimal('250000.00')}
            cars_modelD[c_model['ID_model']] = [c_model['brand_car'], c_model['year_manufactured'], c_model['model_car'], c_model['price_car'], c_model['image_car']]

        for car in cars:
            # {'ID_car': 1, 'model_id': 1, 'license_plate': 'B 1234 ABC', 'availability': 'available'}
            carsD[car['ID_car']] = [car['model_id'], car['license_plate'], car['availability']]
        
        for rental in rentals:
            # {'ID_rental': 1, 'user_id': 1, 'car_id': 1, 'rental_date': datetime.date(2024, 3, 1), 'return_date': datetime.date(2024, 3, 5), 'approval_status': 'approved'}
            rentalsD[rental['ID_rental']] = [rental['user_id'], rental['car_id'], rental['rental_date'], rental['return_date'], rental['approval_status']]

        app.run(debug=True)

    else:
        print("Gagal terhubung ke database.")