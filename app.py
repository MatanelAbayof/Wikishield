from flask import Flask
import toolforge
import json


app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    conn = toolforge.connect('enwiki_p')
    dbs = conn.query("SHOW TABELS")
    return json.dumps(dbs)

# ------------------------------------------ start server --------------------------------------------
if __name__ == '__main__':
    print("Running Wikishield server...")
    app.run(debug=True, use_reloader=False)