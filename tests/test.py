import toolforge
import requests

#toolforge.set_user_agent('wikishield')

import toolforge
args = {
    'host': 'tools.db.svc.eqiad.wmflabs'}
conn = toolforge.connect('s54207__wikishield_p', **args)


with conn.cursor() as cur:
    cur.execute('SHOW DATABASES')
    rows = cur.fetchall()
    print(rows)