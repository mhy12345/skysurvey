from flask import Flask, request, render_template
from star import list_stars, Star

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def home():
    p = int(request.args.get('p', '1'))-1
    stars = {}
    for sname in list_stars()[p*200: (p+1)*200]:
        stars[sname] = Star(sname)
    return render_template('home.html', stars = stars)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
