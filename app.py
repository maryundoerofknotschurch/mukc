from flask import Flask, render_template

app = Flask(__name__)

# Sample announcements
def get_announcements():
    return [
        "Upcoming feast on March 15th!",
        "New choir practice schedule updated.",
        "Lenten season special prayers every Friday."
    ]

@app.route('/')
def home():
    announcements = get_announcements()
    return render_template('index.html', title="Asia’s First Mary Undoer of Knots Church, Thalambur", announcements=announcements)

@app.route('/mass-timings')
def mass_timings():
    return render_template('mass_timings.html', title="Mass Timings")

@app.route('/gallery')
def gallery():
    return render_template('gallery.html', title="Gallery")

@app.route('/contact')
def contact():
    return render_template('contact.html', title="Contact")

# if __name__ == '__main__':
    # app.run("0.0.0.0",port=5001,debug=True)
