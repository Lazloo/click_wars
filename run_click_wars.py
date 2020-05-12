from flask import Flask, render_template, request, jsonify
from pandas.io.json import json_normalize
from click_wars_web_app import click_wars
from flask_cors import CORS

obj_click = click_wars.ClickWars()
obj_click.local_use = True
app = Flask(__name__)
CORS(app)


@app.route('/<int:session_id>')
def session_load(session_id):
    df_session = obj_click.get_list_of_sessions()
    title = df_session.loc[df_session['session_id'] == session_id, 'title'].values[0]
    print(title)
    res = render_template('click_wars.html', session_id=session_id, session_label=title)
    return res


@app.route('/create_session')
def create_session():
    session_label = request.args.get('session_label')
    new_session_id = obj_click.open_new_session(title=session_label)
    return str(new_session_id)


@app.route('/')
def home():
    res = render_template('homepage.html')
    return res


@app.route('/get_session_list')
def get_session_list():
    df_session = obj_click.get_list_of_sessions()
    return df_session.to_json(orient="columns")


@app.route('/get_clicks')
def get_clicks():
    session_id = request.args.get('session_id')
    df_clicks = obj_click.get_clicks(session_id=session_id)
    return df_clicks.to_json(orient="columns")


# /<int: player_id>/<int: session_id>
@app.route('/update_click', methods=['GET'])
def update_click():
    player_id = request.args.get('player_id')
    session_id = request.args.get('session_id')
    obj_click.update_click(player_id=player_id, session_id=session_id)
    return obj_click.get_clicks(session_id=session_id).to_json(orient="columns")
    # return render_template('click_wars.html')


@app.route('/reset_clicks', methods=['GET'])
def reset_clicks():
    session_id = request.args.get('session_id')
    obj_click.reset_clicks(session_id=session_id)
    return obj_click.get_clicks(session_id=session_id).to_json(orient="columns")
    # return render_template('click_wars.html')


if __name__ == '__main__':
    app.run(debug=True, port=10004)
