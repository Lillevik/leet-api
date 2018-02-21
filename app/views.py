from flask import render_template, jsonify, request
import json, os, sqlite3
from app import app


@app.route("/leet")
@app.route("/")
def leet():
    return render_template('leet.html')


@app.route("/leet/score/<serverid>")
def get_leet_json(serverid):
    data = {"scores": []}
    try:
        conn = sqlite3.connect(app.config['DATABASE_PATH'])
        c = conn.cursor()
        query = c.execute("SELECT nick, score, streak, month_score "
                          "FROM Score "
                          "JOIN User on Score.user_id = User.id "
                          "NATURAL JOIN "
                          "      ( "
                          "         SELECT COUNT(streak) as month_score, user_id "
                          "         FROM Graph_data "
                          "         WHERE day BETWEEN datetime('now', 'start of month') "
                          "         AND datetime('now', 'localtime') "
                          "         AND Graph_data.streak > 0 "
                          "         AND Graph_data.server_id = ? "
                          "		    GROUP BY user_id "
                          "	     ) "
                          "WHERE Score.server_id = ? "
                          "ORDER BY month_score desc;", (serverid,serverid,)).fetchall()
        for s in query:
            data["scores"].append({'nick': s[0], 'score': s[1], 'streak': s[2], 'month_score':s[3]})
        conn.close()
    except Exception as e:
        print(e)
    return jsonify(data)


@app.route("/leet/graph/<serverid>")
def get_full_leet_graph(serverid):
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    try:
        data = {}
        c = conn.cursor()
        result = c.execute("SELECT User.nick, Graph_data.day, Graph_data.streak FROM Graph_data "
                           "JOIN User ON Graph_data.user_id = User.id "
                           "WHERE server_id = ?;", (serverid,)).fetchall()
        for day in result:
            if not day[0] in data:
                data[day[0]] = {"graph": []}
            data[day[0]]['graph'].append({"date": day[1], "streak": day[2]})
    except Exception as e:
        return jsonify({"error": "An error occured while fetching data."}), 404
    finally:
        conn.close()
    return jsonify(data)


@app.route("/leet/graph/<serverid>/<nick>")
def get_leet_single_graph_json(serverid, nick):
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    try:
        data = {}
        c = conn.cursor()
        full = request.args.get('full')
        limit = "LIMIT 30"
        if full:
            limit = ""
        result = c.execute("SELECT User.nick, Graph_data.day, Graph_data.streak FROM Graph_data "
                           "JOIN User ON Graph_data.user_id = User.id "
                           "WHERE server_id = ? AND User.nick = ?"
                           "ORDER BY day DESC " + limit + ";", (serverid, nick)).fetchall()
        if not len(result):
            return jsonify({"error": "No data found."}), 404
        for day in result:
            if not day[0] in data:
                data[day[0]] = {"graph": []}
            data[day[0]]['graph'].append({"date": day[1], "streak": day[2]})
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occured while fetching data."}), 500
    finally:
        conn.close()
    return jsonify(data)


@app.route("/leet/graph/average/<serverid>")
def get_avg_leet_graph(serverid):
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    try:
        data = {}
        data['graph'] = []
        c = conn.cursor()
        result = c.execute("SELECT day, AVG(Graph_data.streak) "
                           "FROM Graph_data "
                           "WHERE server_id = ?"
                           "GROUP BY day;", (serverid,)).fetchall()
        for day in result:
            data['graph'].append({'date': day[0], 'avg_streak': day[1]})
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occured while fetching data."}), 404
    finally:
        conn.close()
    return jsonify(data)


@app.route("/leet/graph/average/<serverid>/<nick>")
def get_avg_leet_graph_user(serverid, nick):
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    try:
        data = {}
        data['graph'] = []
        c = conn.cursor()
        result = c.execute("SELECT Count(user_id), AVG(Graph_data.streak), MAX(Graph_data.streak)"
                           "FROM Graph_data "
                           "JOIN User ON User.id = Graph_data.user_id "
                           "WHERE Graph_data.server_id = ? AND User.nick = ?;",(serverid, nick)).fetchall()
        if not len(result):
            return jsonify({'error':'No data found.'}), 404
        for day in result:
            data['graph'].append({'count': day[0], 'avg_streak': day[1], 'max_streak': day[2]})
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occured while fetching data."}), 500
    finally:
        conn.close()
    return jsonify(data)
