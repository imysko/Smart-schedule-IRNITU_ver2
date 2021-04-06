from flask import Flask, request, make_response, jsonify

from functions import find_week, creating_schedule, near_lesson, notifications

app = Flask(__name__)


@app.route('/api/find_week/')
def find_week_route():
    result = find_week.find_week()
    return jsonify(result)


@app.route('/api/creating_schedule/full_schedule_in_str/')
def full_schedule_in_str_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = creating_schedule.full_schedule_in_str(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)


@app.route('/api/creating_schedule/get_one_day_schedule_in_str/')
def get_one_day_schedule_in_str_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = creating_schedule.get_one_day_schedule_in_str(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)


@app.route('/api/creating_schedule/get_next_day_schedule_in_str/')
def get_next_day_schedule_in_str_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = creating_schedule.get_next_day_schedule_in_str(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)

@app.route('/api/creating_schedule/schedule_view_exams/')
def schedule_view_exams():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = creating_schedule.schedule_view_exams(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)

@app.route('/api/creating_schedule/get_one_day_schedule_in_str_prep/')
def get_one_day_schedule_in_str_prep_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = creating_schedule.get_one_day_schedule_in_str_prep(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)


@app.route('/api/creating_schedule/get_next_day_schedule_in_str_prep/')
def get_next_day_schedule_in_str_prep_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = creating_schedule.get_next_day_schedule_in_str_prep(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)


@app.route('/api/creating_schedule/full_schedule_in_str_prep/')
def full_schedule_in_str_prep_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = creating_schedule.full_schedule_in_str_prep(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)


@app.route('/api/near_lesson/get_near_lesson/')
def get_near_lesson_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = near_lesson.get_near_lesson(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)


@app.route('/api/near_lesson/get_now_lesson/')
def get_now_lesson_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = near_lesson.get_now_lesson(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)


@app.route('/api/creating_schedule/get_now_lesson_in_str_stud/')
def get_now_lesson_in_str_stud_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = creating_schedule.get_now_lesson_in_str_stud(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)



@app.route('/api/creating_schedule/get_now_lesson_in_str_prep/')
def get_now_lesson_in_str_prep_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = creating_schedule.get_now_lesson_in_str_prep(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)


@app.route('/api/notifications/calculating_reminder_times/')
def calculating_reminder_times_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = notifications.calculating_reminder_times(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)


@app.route('/api/notifications/get_notifications_status/')
def get_notifications_status_route():
    data = request.json
    if not data:
        return make_response("Bad request", 400)
    try:
        result = notifications.get_notifications_status(**data)
    except TypeError:
        return make_response("Bad request", 400)
    return jsonify(result)
