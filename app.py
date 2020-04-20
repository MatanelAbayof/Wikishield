from flask import Flask
import toolforge
import json


app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    conn = toolforge.connect('enwiki_p')
    with conn.cursor() as cur:
        cur.execute('SHOW TABLES')
        rows = cur.fetchall()
        print(rows)
    return json.dumps(rows)

# ------------------------------------------ start server --------------------------------------------
if __name__ == '__main__':
    print("Running Wikishield server...")
    app.run(debug=True, use_reloader=False)