


from flask import Flask, render_template, request


app = Flask(__name__)

@app.route('/')
def main():
    return render_template('maryundoerofknots.html')

@app.route('/maryundoerofknots_home', methods=['GET','POST'])
def MUKC_home(result=None):
    pass



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='localhost',port=5000,debug=True)

