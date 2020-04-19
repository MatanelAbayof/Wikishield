from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return "Hello!"

# ------------------------------------------ start server --------------------------------------------
if __name__ == '__main__':
    print("Running Wikishield server...")
    app.run(debug=True, use_reloader=False)