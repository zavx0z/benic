from flask import jsonify, request

from app.period.serialize import periods_schema
from app.task.models import Task
from app.period import period
from app.period.models import Period


@period.route('/periods', methods=['GET'])
def get_periods():
    session = request.args.get('session')
    count = request.args.get('count')
    task = Task.query.filter_by(session=session).first()
    if not task:
        return jsonify({"error": "задачи не существует"})
    elif count:
        count = int(count)
        periods = Period.query.order_by(Period.id.desc()).limit(count).all()
    else:
        periods = Period.all()
    return jsonify(periods_schema.dump(periods))
