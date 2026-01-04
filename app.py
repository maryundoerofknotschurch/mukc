from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'frvinoth@july18'

NEWS_FILE = 'data/news.csv'
SCHEDULE_FILE = 'data/schedule.csv'
CONTACT_CSV = 'data/contact_submissions.csv'
DONATE_CSV = 'data/donation_submissions.csv'
os.makedirs('data', exist_ok=True)

from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'maryundoerofknotschurch@gmail.com'  # Sender Gmail
app.config['MAIL_PASSWORD'] = 'dkqyodpdwxadiwkg'     # Gmail App Password (not Gmail password)

mail = Mail(app)

# Email addresses to block
BLACKLISTED_EMAILS = {'spammer@example.com', 'bot@spam.com', 'badguy@mail.com'}


from werkzeug.utils import secure_filename

UPLOAD_NEWS = 'static/uploads/news'
UPLOAD_SCHEDULE = 'static/uploads/schedule'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_NEWS, exist_ok=True)
os.makedirs(UPLOAD_SCHEDULE, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





@app.route('/')
def home():
    news = []
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            news = list(reader)

    schedule = []
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            schedule = list(reader)

    return render_template("home.html", news=news, schedule=schedule)


@app.route('/gallery')
def gallery():
    # Redirect to #gallery section on home
    return redirect(url_for('home') + '#gallery')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            flash("Logged in as admin.", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('home'))


# @app.route('/add_news', methods=['POST'])
# def add_news():
#     if not session.get('admin'):
#         flash("Unauthorized access.", "danger")
#         return redirect(url_for('home'))

#     title = request.form.get('title', '').strip()
#     content = request.form.get('content', '').strip()

#     if title and content:
#         with open(NEWS_FILE, 'a', newline='', encoding='utf-8') as f:
#             writer = csv.DictWriter(f, fieldnames=['title', 'content'])
#             if f.tell() == 0:
#                 writer.writeheader()
#             writer.writerow({'title': title, 'content': content})
#         flash("News added.", "success")
#     else:
#         flash("Title and content are required.", "warning")

#     return redirect(url_for('home') + '#news')


@app.route('/add_news', methods=['POST'])
def add_news():
    if not session.get('admin'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('home'))

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    image_file = request.files.get('image')

    filename = ''
    if image_file and image_file.filename and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(UPLOAD_NEWS, filename))

    if title and content:
        with open(NEWS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'content', 'image'])
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow({
                'title': title,
                'content': content,
                'image': filename
            })
        flash("News added.", "success")

    return redirect(url_for('home') + '#news')


@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    if not session.get('admin'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('home'))

    day = request.form.get('day', '').strip()
    time = request.form.get('time', '').strip()
    details = request.form.get('details', '').strip()

    if day and time and details:
        with open(SCHEDULE_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['day', 'time', 'details'])
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow({'day': day, 'time': time, 'details': details})
        flash("Schedule added.", "success")
    else:
        flash("All fields are required.", "warning")

    return redirect(url_for('home') + '#schedule')


@app.route('/donate', methods=['POST'])
def donate():
    name = request.form.get('first_name')
    mobile = request.form.get('mobile')
    # amount = request.form.get('amount')
    email = request.form.get('email')
    city = request.form.get('city')
    comment = request.form.get('comment')

    # Check required fields (you can adjust which ones are required)
    # if not name or not mobile or not amount or not city:
    #     flash("Please fill all required fields (Name, Mobile, Amount, City).", "danger")
    #     return redirect(url_for('home') + '#donate')
    if not name or not mobile or not city:
        flash("Please fill all required fields (Name, Mobile, City).", "danger")
        return redirect(url_for('home') + '#donate')

    # Block blacklisted emails
    if email in BLACKLISTED_EMAILS:
        # flash("Sorry, donations from this email are not accepted.", "danger")
        return redirect(url_for('home') + '#donate')

    # with open(DONATE_CSV, 'a', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerow([datetime.now(), name, mobile, email, city, amount, comment])
    # Ensure headers are written if the file doesn't exist or is empty
    file_exists = os.path.exists(DONATE_CSV)
    write_header = not file_exists or os.path.getsize(DONATE_CSV) == 0

    with open(DONATE_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['Date', 'Name', 'Mobile', 'Email', 'City', 'Comment'])
        writer.writerow([datetime.now().date(), name, mobile, email, city, comment])

    body = f"""
    New Donation Request Received

    Name: {name}
    Mobile: {mobile}
    Email: {email}
    City: {city}
    Comment: {comment}
    """

    msg = Message("New Donation", sender=app.config['MAIL_USERNAME'],
                  recipients=['maryundoerofknotschurch@gmail.com'], body=body)
    mail.send(msg)

    # flash("Thank you for your donation Request!", "success")
    return redirect(url_for('home') + '#donate')

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # Basic required field check
    if not name or not email or not message:
        flash("Please fill all the required fields (Name, Email, and Message).", "danger")
        return redirect(url_for('home') + '#contact')

    # Block blacklisted emails
    if email in BLACKLISTED_EMAILS:
        # flash("Sorry, submissions from this email are not accepted.", "danger")
        return redirect(url_for('home') + '#contact')

    # Save to CSV
    # with open(CONTACT_CSV, 'a', newline='') as f:
    #     writer = csv.writer(f)
        # writer.writerow([datetime.now(), name, email, subject, message])
    # Save to CSV with header check
    file_exists = os.path.exists(CONTACT_CSV)
    write_header = not file_exists or os.stat(CONTACT_CSV).st_size == 0

    with open(CONTACT_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['Date', 'Name', 'Email', 'Subject', 'Message'])
        writer.writerow([datetime.now().date(), name, email, subject, message])

    body = f"""
    New Contact Message

    Name: {name}
    Email: {email}
    Subject: {subject}
    Message: {message}
    """

    msg = Message("New Contact Message", sender=app.config['MAIL_USERNAME'],
                  recipients=['maryundoerofknotschurch@gmail.com'], body=body)
    mail.send(msg)

    # flash("Message sent successfully!", "success")
    return redirect(url_for('home') + '#contact')

# @app.route('/donate', methods=['POST'])
# def donate():
#     name = request.form.get('first_name')
#     mobile = request.form.get('mobile')
#     amount = request.form.get('amount')
#     email = request.form.get('email')
#     city = request.form.get('city')
#     comment = request.form.get('comment')

#     body = f"""
#     New Donation Received

#     Name: {name}
#     Mobile: {mobile}
#     Email: {email}
#     City: {city}
#     Amount: ₹{amount}
#     Comment: {comment}
#     """

#     msg = Message("New Donation", sender=app.config['MAIL_USERNAME'],
#                   recipients=['maryundoerofknotschurch@gmail.com'], body=body)
#     mail.send(msg)

#     flash("Thank you for your donation!", "success")
#     return redirect(url_for('home') + '#donate')

# @app.route('/contact', methods=['POST'])
# def contact():
#     name = request.form.get('name')
#     email = request.form.get('email')
#     subject = request.form.get('subject')
#     message = request.form.get('message')

#     body = f"""
#     New Contact Message

#     Name: {name}
#     Email: {email}
#     Subject: {subject}
#     Message: {message}
#     """

#     msg = Message("New Contact Message", sender=app.config['MAIL_USERNAME'],
#                   recipients=['maryundoerofknotschurch@gmail.com'], body=body)
#     mail.send(msg)

#     flash("Message sent successfully!", "success")
#     return redirect(url_for('home') + '#contact')


@app.route('/delete_news/<int:index>', methods=['POST'])
def delete_news(index):
    if not session.get('admin'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('home'))

    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, newline='', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))

        if 0 <= index < len(reader):
            if reader[index].get('image'):
                path = os.path.join(UPLOAD_NEWS, reader[index]['image'])
                if os.path.exists(path):
                    os.remove(path)
                    
            del reader[index]
            with open(NEWS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['title', 'content'])
                writer.writeheader()
                writer.writerows(reader)
            flash("News entry deleted.", "success")
        else:
            flash("Invalid entry index.", "warning")

    return redirect(url_for('home') + '#news')


@app.route('/delete_schedule/<int:index>', methods=['POST'])
def delete_schedule(index):
    if not session.get('admin'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('home'))

    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, newline='', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))

        if 0 <= index < len(reader):
            del reader[index]
            with open(SCHEDULE_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['day', 'time', 'details'])
                writer.writeheader()
                writer.writerows(reader)
            flash("Schedule entry deleted.", "success")
        else:
            flash("Invalid entry index.", "warning")

    return redirect(url_for('home') + '#schedule')


from flask import session, abort
from flask import render_template
@app.route("/admin/dashboard")
def admin_dashboard():
    contact_csv = os.path.join(app.root_path, 'data', 'contact_submissions.csv')
    donate_csv = os.path.join(app.root_path, 'data', 'donation_submissions.csv')

    contact_data = []
    donate_data = []
    contact_headers = []
    donate_headers = []

    # Process Contact CSV
    if os.path.exists(contact_csv):
        with open(contact_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contact_headers = reader.fieldnames or []
            contact_data = list(reader)

    # Process Donate CSV
    if os.path.exists(donate_csv):
        with open(donate_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            donate_headers = reader.fieldnames or []
            donate_data = list(reader)

    return render_template("admin_dashboard.html",
                           contact_data=contact_data,
                           donate_data=donate_data,
                           contact_headers=contact_headers,
                           donate_headers=donate_headers)



import os
import csv
from flask import redirect, url_for, flash

@app.route('/delete-contact/<int:index>')
def delete_contact(index):
    file_path = os.path.join(app.root_path, 'data', 'contact_submissions.csv')

    if os.path.exists(file_path):
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            headers = reader.fieldnames or []

        if 0 <= index < len(rows):
            del rows[index]
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
            # flash('Contact entry deleted successfully.', 'success')
        else:
            # flash('Invalid contact index.', 'danger')
            print("Invalid contact index.")
    else:
        # flash('Contact file not found.', 'danger')
        print("Contact file not found.")

    return redirect(url_for('admin_dashboard'))


@app.route('/delete-donate/<int:index>')
def delete_donate(index):
    file_path = os.path.join(app.root_path, 'data', 'donation_submissions.csv')

    if os.path.exists(file_path):
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            headers = reader.fieldnames or []

        if 0 <= index < len(rows):
            del rows[index]
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
            flash('Donation entry deleted successfully.', 'success')
        else:
            flash('Invalid donation index.', 'danger')
    else:
        flash('Donation file not found.', 'danger')

    return redirect(url_for('admin_dashboard'))

# if __name__ == '__main__':
    # app.run("0.0.0.0",port=5001,debug=True)

