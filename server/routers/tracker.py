from server import api
from flask import request, jsonify
from server.models.tracker import Tracker
from datetime import datetime

@api.route('/user/<username>/steps', methods=['POST'])
def tracker(username):

    data = request.get_json()

    date = data.get('date')
    steps = data.get('steps')

    if date:
        date = datetime.strftime(date, "%Y-%m-%d")

    if steps < 0:
        return
        
    instance = Tracker(username = username, date = date, steps = steps)
    instance.save()

    return jsonify({"message": "steps count updated"}), 200