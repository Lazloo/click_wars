from flask import Flask, render_template, request, jsonify
from pandas.io.json import json_normalize
from click_wars_web_app import click_wars
from flask_cors import CORS

obj_click = click_wars.ClickWars()
app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    res = render_template('click_wars.html')
    return res


@app.route('/get_clicks')
def get_clicks():
    df_clicks = obj_click.get_clicks(session_id=1)
    # request.form.
    # return render_template('click_wars.html')
    return df_clicks.to_json(orient="columns")
    # return df_clicks.to_json(orient="values")
    # return json_normalize(df_clicks.to_dict())


@app.route('/update_progress_bar')
def update_progress_bar():
    result_bar = request.form.getlist('result_bar')
    df_clicks = obj_click.get_clicks(session_id=1)
    return render_template('click_wars.html')


# /<int: player_id>/<int: session_id>
@app.route('/update_click', methods=['POST', 'GET'])
def update_click():
    print('update')
    player_id = request.args.get('player_id')
    session_id = request.args.get('session_id')
    obj_click.update_click(player_id=player_id, session_id=session_id)
    return render_template('click_wars.html')


if __name__ == '__main__':
    app.run(debug=True, port=10004)
