from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

NEWS_FILE = 'data/news.csv'
SCHEDULE_FILE = 'data/schedule.csv'
os.makedirs('data', exist_ok=True)

from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'maryundoerofknotschurch@gmail.com'  # Sender Gmail
app.config['MAIL_PASSWORD'] = 'dkqyodpdwxadiwkg'     # Gmail App Password (not Gmail password)

mail = Mail(app)


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


@app.route('/add_news', methods=['POST'])
def add_news():
    if not session.get('admin'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('home'))

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()

    if title and content:
        with open(NEWS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'content'])
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow({'title': title, 'content': content})
        flash("News added.", "success")
    else:
        flash("Title and content are required.", "warning")

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
    amount = request.form.get('amount')
    email = request.form.get('email')
    city = request.form.get('city')
    comment = request.form.get('comment')

    body = f"""
    New Donation Received

    Name: {name}
    Mobile: {mobile}
    Email: {email}
    City: {city}
    Amount: ₹{amount}
    Comment: {comment}
    """

    msg = Message("New Donation", sender=app.config['MAIL_USERNAME'],
                  recipients=['maryundoerofknotschurch@gmail.com'], body=body)
    mail.send(msg)

    flash("Thank you for your donation!", "success")
    return redirect(url_for('home') + '#donate')

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

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

    flash("Message sent successfully!", "success")
    return redirect(url_for('home') + '#contact')


@app.route('/delete_news/<int:index>', methods=['POST'])
def delete_news(index):
    if not session.get('admin'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('home'))

    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, newline='', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))

        if 0 <= index < len(reader):
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


# if __name__ == '__main__':
    # app.run("0.0.0.0",port=5001,debug=True)
