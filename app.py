from flask import  *
from auth import *
from database_setup import init_db
import datetime
from heap import *
import sqlite3  
from inventory_management import *
from sms import *
from forecast import calculate_product_forecasts
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-fallback-key')
 

init_db()

@app.after_request
def add_header(response):
    """
    Forces the user's browser to download a fresh copy of the page 
    from the server instead of reading a dead snapshot from the local cache.
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



def get_expiry_context():
    """Returns today's date strings used for expiry comparison in templates."""
    today = datetime.date.today()
    warn_date    = today + datetime.timedelta(days=10)    
    caution_date = today + datetime.timedelta(days=30)    
    return {
        'today_date'        : today.strftime('%Y-%m-%d'),
        'expiry_warn_date'  : warn_date.strftime('%Y-%m-%d'),
        'expiry_caution_date': caution_date.strftime('%Y-%m-%d'),
    }


@app.route('/')
def home():
    if session.get('email'):
        email         = session.get('email')
        load_from_db(email)
        inventory     = get_all_inventory(email=email)    
        expiring_items = get_expiring_stocks(email=email)
        forecast_data = calculate_product_forecasts(email=email)
        ctx           = get_expiry_context()
        user_products = get_user_products_summary(email=email)
        return render_template(
            'dashboard.html',
            inventory      = inventory,
            expiring_items = expiring_items,
            forecast_data  = forecast_data,
            user_products  = user_products,
            **ctx
        )
    return render_template('landing_page.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        
        print("In register function")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE email = ?",(email,))
        is_already_registered = cursor.fetchall()
        if( is_already_registered ) :
            flash("Email already registered.\n Go to log in.",'danger')
            conn.commit()
            conn.close()

        else : 
            otp = generate_otp()
            
            
            session['temp_user'] = {
                'email': email,
                'password': password,
                'name': name,
                'otp': otp,
                'mobile' : mobile
            }
            
            if send_otp_email(email, otp, name):
                flash("An OTP has been generated. Check your email, or check the terminal console if SMTP is not configured in .env.", "info")
                return redirect(url_for('verify_otp_page'))

            else:
                flash("Error sending OTP email. Please try again.", "danger")
            
    return render_template('register.html')



@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    
    print("in verify otp function")
    if 'temp_user' not in session:
        return redirect(url_for('register'))
        
    if request.method == 'POST':
        user_entered_otp = request.form.get('otp')
        temp_data = session['temp_user']
        
         
        if user_entered_otp == temp_data['otp']:
             
            try:
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO user (email, password, name, mobile) VALUES (?, ?, ?, ?)", 
                    (temp_data['email'], temp_data['password'], temp_data['name'], temp_data['mobile'])
                )
                conn.commit()
                conn.close()
            

                is_registered = send_registration_alert(temp_data['name'], temp_data['email'])
                 

                flash("Registration successful! You can now log in.", "success")
                session.pop('temp_user', None)

                return redirect(url_for('login_route'))
            except Exception as e:
                flash("Database error occurred, contact developer", "danger")
                print(e)
        else:
             
            flash("Invalid OTP code. Please look closely and try again.", "danger")
            
    return render_template('verify_otp.html')



@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'GET':
        return render_template('login.html')

    email    = request.form.get('email')
    password = request.form.get('password')

    if login(email=email, password=password):
        session['email'] = email
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error="Invalid email or password. Please try again.")



@app.route('/add_batch', methods=['GET', 'POST'])
def add_batchs():
    if not session.get('email'):
        return redirect(url_for('login_route'))

    email = session.get('email')
    if request.method == 'GET':
        user_products = get_user_products_summary(email=email)
        return render_template('add.html', user_products=user_products)

    batch_no     = request.form.get('batch_no')
    product_name = request.form.get('product_name')
    try:
        quantity = int(request.form.get('quantity', 0))
    except (ValueError, TypeError):
        quantity = 0
    expiry_date  = request.form.get('expiry_date')
    try:
        unit_price = float(request.form.get('unit_price', 0.0) or 0.0)
    except (ValueError, TypeError):
        unit_price = 0.0

    print("in add_batch in app.py")
    if add_batch(email, product_name, batch_no, quantity, expiry_date, unit_price=unit_price, allow_increment=True):
        flash(f"Batch {batch_no} successfully recorded!", "success")
        return redirect(url_for('home'))
    return render_template('error_add.html', error = "Error adding batch. Ensure you enter a valid quantity and expiry date. Please go back and try again.")


@app.route('/adjust_product', methods=['POST'])
def adjust_product_route():
    if not session.get('email'):
        return redirect(url_for('login_route'))

    email        = session.get('email')
    product_name = request.form.get('product_name')
    batch_no     = request.form.get('batch_no')
    action_type  = request.form.get('action_type', 'increase') # 'increase', 'decrease', or 'price_only'
    price_str    = request.form.get('unit_price')
    unit_price   = None
    if price_str is not None and price_str.strip() != "":
        try:
            unit_price = float(price_str)
        except ValueError:
            unit_price = None

    if action_type == 'price_only':
        delta = 0
    else:
        try:
            qty = int(request.form.get('quantity', 0))
        except (ValueError, TypeError):
            qty = 0
        delta = qty if action_type == 'increase' else -qty

    success, msg, _ = adjust_product_stock(
        email=email,
        product_name=product_name,
        delta_qty=delta,
        batch_no=batch_no,
        unit_price=unit_price
    )
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    redirect_to = request.form.get('redirect_to', 'home')
    if redirect_to == 'add_batch':
        return redirect(url_for('add_batchs'))
    return redirect(url_for('home'))


@app.route('/adjust_batch/<batch_no>', methods=['POST'])
def adjust_batch_route(batch_no):
    if not session.get('email'):
        return redirect(url_for('login_route'))
    email = session.get('email')
    delta_str = request.form.get('delta', '1')
    try:
        delta = int(delta_str)
    except (ValueError, TypeError):
        delta = 1

    new_qty = adjust_batch_quantity(email=email, batch_no=batch_no, delta_qty=delta)
    if new_qty is not None:
        if new_qty == 0:
            flash(f"Batch {batch_no} depleted and deleted.", "info")
        else:
            flash(f"Batch {batch_no} quantity updated to {new_qty}.", "success")
    else:
        flash(f"Failed to adjust batch {batch_no}.", "danger")
    return redirect(url_for('home'))


@app.route('/edit_batch/<batch_no>', methods=['POST'])
def edit_batch_route(batch_no):
    if not session.get('email'):
        return redirect(url_for('login_route'))
    email = session.get('email')
    qty_str = request.form.get('quantity')
    price_str = request.form.get('unit_price')
    expiry_str = request.form.get('expiry_date')

    quantity = int(qty_str) if qty_str and qty_str.isdigit() else None
    unit_price = None
    if price_str is not None and price_str.strip() != "":
        try:
            unit_price = float(price_str)
        except ValueError:
            unit_price = None
    expiry_date = expiry_str.strip() if expiry_str else None

    if edit_batch(email=email, batch_no=batch_no, quantity=quantity, unit_price=unit_price, expiry_date=expiry_date):
        flash(f"Batch {batch_no} updated successfully.", "success")
    else:
        flash(f"Could not update batch {batch_no}. Please verify inputs.", "danger")
    return redirect(url_for('home'))


@app.route('/sell_product', methods=['GET', 'POST'])
def sell_product_route():
    if not session.get('email'):
        return redirect(url_for('login_route'))

    if request.method == 'GET':
        return render_template('sell.html')

    email        = session.get('email')
    product_name = request.form.get('product_name')
    quantity     = int(request.form.get('quantity'))

    if sell_product(email=email, product_name=product_name, quantity=quantity):
        flash(f"Sold {quantity} units of {product_name} successfully via FEFO.", "success")
        return redirect(url_for('home'))
    return render_template('error_sell.html', error = "Error selling batch. Insufficient non-expired stock. Please go back and try again.")


@app.route('/get_expiring_stock')
def get_expiring_stock_route():
    if not session.get('email'):
        return redirect(url_for('login_route'))

    email          = session.get('email')
    load_from_db(email)
    inventory      = get_all_inventory(email=email)
    expiring_items = get_expiring_stocks(email=email)
    forecast_data  = calculate_product_forecasts(email=email)
    ctx            = get_expiry_context()
    return render_template(
        'dashboard.html',
        inventory      = inventory,
        expiring_items = expiring_items,
        forecast_data  = forecast_data,
        **ctx
    )


@app.route('/delete_batch/<batch_no>', methods=['POST'])
def delete_batch_route(batch_no):
    if not session.get('email'):
        return redirect(url_for('login_route'))
    email = session.get('email')
    if delete_batch(email=email, batch_no=batch_no):
        flash(f"Batch {batch_no} deleted.", "info")
    else:
        flash(f"Failed to delete batch {batch_no}.", "danger")
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


 

if __name__ == '__main__':
    app.run(debug=True)
