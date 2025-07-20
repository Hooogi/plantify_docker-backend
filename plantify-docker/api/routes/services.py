import mariadb
from flask import current_app, jsonify, Response
from contextlib import contextmanager
from .endpoint_configs import ENDPOINT_CONFIGS

@contextmanager
def db_cursor():
    connection = mariadb.connect(**current_app.config['DB_CONFIG'])
    cursor = connection.cursor(dictionary=True)
    try:
        yield connection, cursor
    finally:
        cursor.close()
        connection.close()

def run_query(query, param_values, operation):
    try:
        with db_cursor() as (conn, cursor):
            cursor.execute(query, tuple(param_values.values()))
            if operation == "fetch":
                return jsonify(cursor.fetchall())
            elif operation == "fetchone":
                return jsonify(cursor.fetchone())
            elif operation in {"insert", "update", "delete"}:
                conn.commit()
                result = {'success': True}
            else:
                return jsonify({'error': f'Unknown operation: {operation}'}), 400
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handle_db_action(endpoint, params, action_type):
    query = ENDPOINT_CONFIGS[endpoint]["query"]

    if action_type == "json":
        allowed_params = {"pot_id", "user_mail"}
        if len(params) != 1 or not set(params.keys()).issubset(allowed_params):
            return Response("Exactly one valid parameter required", status=400)
        param_value = next(iter(params.items()))[1]
        return run_query(query, {"value": param_value}, "fetch")

    elif action_type in {"insert", "update", "delete"}:
        expected_keys = ENDPOINT_CONFIGS[endpoint].get("params", [])
        if not set(expected_keys).issubset(params.keys()):
            return Response("Missing or unexpected parameters", status=400)
        filtered = {k: params[k] for k in expected_keys}
        return run_query(query, filtered, operation=action_type)

    return Response("Unknown action type", status=400)