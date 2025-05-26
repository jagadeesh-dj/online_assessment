from server import api
from flask import request, jsonify
from server.models.tracker import Tracker
from datetime import datetime
from sqlalchemy import and_

@api.route('/user/<username>/steps', methods=['POST'])
def tracker(username):

    data = request.get_json()

    date = data.get('date')
    steps = data.get('steps')

    if date:
        date = datetime.strftime(date, "%Y-%m-%d")

    if steps>0:
        instance = Tracker.query.filter(and_(Tracker.username==username, Tracker.date==date)).first()
        if instance:
            instance.steps=steps
            instance.save()
        else:
            instance.username=username
            instance.date=date
            instance.steps=steps
            instance.save()

    return jsonify({"message": "steps count updated"}), 200