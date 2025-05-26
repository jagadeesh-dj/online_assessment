from server import api
from flask import request, jsonify
from server.models.tracker import Tracker

@api.route('/user/<username>/steps', methods=['POST'])
def tracker(username):

    data = request.get_json()

    date = data.get('date')
    steps = data.get('steps')

    instance = Tracker(username = username, date = date, steps = steps)
    instance.save()

    return jsonify({"message": "steps count updated"}), 200