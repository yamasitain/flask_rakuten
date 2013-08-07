import sqlite3, os, urllib2, json
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from datetime import date

DATABASE = '/tmp/ritem.db'
DEBUG = True

APPLICATIONID = 'xxxxxx'
APPSECRET   = 'xxxxx'
AFFILIATEID = 'xxxxx'

SECRET_KEY  = 'development key'
USERNAME    = 'admin'
PASSWORD    = 'default'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTING', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.route('/')
def show_entries():
    cur = g.db.execute('select name, catch, code, url, imgurl from ritem order by id desc')
    entries = [dict(name=row[0], catch=row[1], code=row[2], url=row[3], imgurl=row[4]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'] )
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    if not request.form['q'] :
        return redirect(url_for('show_entries'))
    host = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20130805?"
    req = [
        "applicationId=" + app.config['APPLICATIONID'],
        "affiliateId=" + app.config['AFFILIATEID'],
        "keyword=" + request.form['q'],
    ]
    uri = host + "&".join(req)
    res = json.load(urllib2.urlopen(uri))
#    res = json.load(urllib2.urlopen("https://app.rakuten.co.jp/services/api/IchibaItem/Search/20130805?format=json&keyword=test&applicationId=107a31b9eb9988703189fea16cdf1bcc"))
#    items = res["Body"]["ItemSearch"]["Items"]["Item"]
    items = res['Items']

    for item in items :
        if item['Item']['availability'] == 1 :
            g.db.execute('insert into ritem (name, catch, code, url, imgurl, shopcode, genreid, date) values (?, ?, ?, ?, ?, ?, ?, ?)',
                [item['Item']['itemName'], item['Item']['catchcopy'], item['Item']['itemCode'], item['Item']['affiliateUrl'], item['Item']['mediumImageUrls'][0]['imageUrl'], item['Item']['shopCode'], item['Item']['genreId'], date.today()])
            g.db.commit()
        
        g.db.execute('insert into rshop (itemcode, shopcode, shopname, shopurl, genreid, date) values (?, ?, ?, ?, ?, ?)',
            [item['Item']['itemCode'], item['Item']['shopCode'], item['Item']['shopName'], item['Item']['shopUrl'], item['Item']['genreId'], date.today()])
        g.db.commit()

        for imageUrl in item['Item']['mediumImageUrls'] :
            g.db.execute('insert into rwindow (itemcode, shopcode, genreid, itemurl, imgurl, date) values (?, ?, ?, ?, ?, ?)',
                [item['Item']['itemCode'], item['Item']['shopCode'],  item['Item']['genreId'], item['Item']['affiliateUrl'], imageUrl['imageUrl'], date.today()])
            g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalie username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalied password'
        else:
            session['logged_in'] = True
            flash('Yow were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

    



@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

if __name__ == '__main__':
    port=int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0')
