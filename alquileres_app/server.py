from bson import ObjectId
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask.json import JSONEncoder
from flask_pymongo import PyMongo


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return JSONEncoder.default(self, obj)


app = Flask('alquileres')

app.config['MONGO_DBNAME'] = 'alquileres'
app.config['MONGO_URI'] = 'mongodb://172.17.0.2:27017'

app.json_encoder = CustomJSONEncoder

mongo = PyMongo(app)


@app.route('/api/alquileres/', methods=['GET'])
def get_all_offers():
    offers = mongo.db.alquileres_ofrecidos
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 0))
    skip = (page - 1) * limit
    filters = {
        'discarded': False,
        'address': {'$ne': None},
        'maps_place_id': {'$ne': 'ChIJ7wpe-SbfbA0Rw1aEEOjS8U0'},
        'location': {'$ne': None}
    }
    output = []
    for offer in offers.find(filters).skip(skip).limit(limit):
        offer['html'] = render_template('offer.html', offer=offer)
        offer['title'] = offer['address']
        output.append(offer)
    return jsonify({'result' : output})


@app.route('/api/alquiler/<string:_id>', methods=['GET', 'DELETE', 'PUT'])
def get_offer(_id):
    offers = mongo.db.alquileres_ofrecidos
    offer = offers.find_one(ObjectId(_id))
    if request.method == 'DELETE':
        offer['discarded'] = True
        offers.update_one(
            {'_id': ObjectId(_id)},
            {"$set": {"discarded": True}},
            upsert=False
        )
    elif request.method == 'PUT':
        offer['interesting'] = True
        offers.update_one(
            {'_id': ObjectId(_id)},
            {"$set": {"interesting": True}},
            upsert=False
        )
    return jsonify({'result': offer})


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


def format_html(offer):
    return HTML_TEMPLATE.format(**offer)

if __name__ == '__main__':
    app.run(debug=True)
