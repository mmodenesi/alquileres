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
EXCLUDED_TYPE_OF_NEIGHBOURHOODS = ['Country', 'Cerrado', 'Con Seguridad']


ALLOWED_LOCATIONS = (
    (-31.394702925950813, -64.21810833740233, -31.432196906742682, -64.22824270629889),
    (-31.402322175343983, -64.20798666381842, -31.428095617178545, -64.21810833740233),
    (-31.40408037583773, -64.19871694946295,  -31.420624950214414, -64.20918194580076),
)


@app.route('/api/alquileres/', methods=['GET'])
def get_all_offers():
    offers = mongo.db.alquileres_ofrecidos
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 0))
    skip = (page - 1) * limit
    filters = {
        'discarded': False,
        'type_of_neighbourhood': {
            "$nin": EXCLUDED_TYPE_OF_NEIGHBOURHOODS
        },
        # 'address': {'$ne': None},
        # 'location': {'$ne': {'lat': 0, 'lng': 0}}
    }
    output = []
    for offer in offers.find(filters).skip(skip).limit(limit):
        try:
            lat, lng = offer['location']['lat'], offer['location']['lng']
        except KeyError:
            offer['location'] = {'lat': 0, 'lng': 0}
        not_too_far = any((x1 <= lat <= x2) and (y1 <= lng <= y2)
                          for x2, y2, x1, y1 in ALLOWED_LOCATIONS)
        if True or not_too_far:
            offer['html'] = render_template('offer.html', offer=offer)
            offer['title'] = offer['address']
            output.append(offer)
    return jsonify({'result' : output})


@app.route('/api/alquiler/<string:_id>$', methods=['GET'])
def get_offer(_id):
    offers = mongo.db.alquileres_ofrecidos
    offer = offers.find_one(ObjectId(_id))
    return jsonify({'result': offer})


@app.route('/api/alquiler/<string:_id>/discard', methods=['PUT'])
def set_discarded_true(_id):
    offers = mongo.db.alquileres_ofrecidos
    offer = offers.find_one(ObjectId(_id))
    if offer:
        offer['discarded'] = True
        offers.update_one(
            {'_id': ObjectId(_id)},
            {"$set": {"discarded": True}},
            upsert=False
        )
    return jsonify({'result': offer})


@app.route('/api/alquiler/<string:_id>/pin', methods=['PUT'])
def set_interesting_true(_id):
    offers = mongo.db.alquileres_ofrecidos
    offer = offers.find_one(ObjectId(_id))
    if offer:
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
