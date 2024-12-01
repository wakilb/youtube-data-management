from flask import Flask, jsonify, request, send_from_directory
import psycopg
from pymongo import MongoClient

app = Flask(__name__)

# PostgreSQL Connection
def connect_postgres():
    return psycopg.connect(
        dbname="youtube_data",
        user="postgres",
        password="your_postgres_password",
        host="localhost",
        port=5432
    )

# MongoDB Connection
def connect_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    return client["youtube_data"]

# 1. Fetch Data
@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    try:
        database = request.args.get('database')
        table = request.args.get('table')

        results = {}

        # Fetch from PostgreSQL
        if database in ['postgres', 'both']:
            pg_conn = connect_postgres()
            with pg_conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {table};")
                pg_results = cur.fetchall()
                results['PostgreSQL'] = pg_results
            pg_conn.close()

        # Fetch from MongoDB
        if database in ['mongo', 'both']:
            mongo_db = connect_mongo()
            mongo_results = list(mongo_db[table].find())
            for doc in mongo_results:
                doc["_id"] = str(doc["_id"])
            results['MongoDB'] = mongo_results

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Insert Data
@app.route('/insert_data', methods=['POST'])
def insert_data():
    try:
        database = request.args.get('database')
        table = request.json['table']
        data = request.json['data']

        results = {}

        # Insert into PostgreSQL
        if database in ['postgres', 'both']:
            pg_conn = connect_postgres()
            with pg_conn.cursor() as cur:
                if table == 'Videos':
                    if 'email' in data:
                        cur.execute("SELECT user_id FROM Users WHERE email = %s", (data['email'],))
                        user = cur.fetchone()

                        if not user:
                            cur.execute(
                                "INSERT INTO Users (name, email, region) VALUES (%s, %s, %s) RETURNING user_id",
                                (data.get('name', 'Unknown'), data['email'], data.get('region', 'Unknown'))
                            )
                            user_id = cur.fetchone()[0]
                        else:
                            user_id = user[0]
                    elif 'user_id' in data:
                        user_id = data['user_id']
                    else:
                        raise ValueError("Either 'email' or 'user_id' must be provided.")
                    
                    cur.execute(
                        "INSERT INTO Videos (title, description, upload_date, category, user_id) VALUES (%s, %s, %s, %s, %s) RETURNING video_id",
                        (data['title'], data['description'], data['upload_date'], data['category'], user_id)
                    )
                    results['PostgreSQL'] = f"Video inserted with video_id: {cur.fetchone()[0]}"
                elif table == 'Users':
                    cur.execute(
                        "INSERT INTO Users (name, email, region) VALUES (%s, %s, %s) RETURNING user_id",
                        (data['name'], data['email'], data['region'])
                    )
                    results['PostgreSQL'] = f"User inserted with user_id: {cur.fetchone()[0]}"

                pg_conn.commit()
            pg_conn.close()

        # Insert into MongoDB
        if database in ['mongo', 'both']:
            mongo_db = connect_mongo()
            result = mongo_db[table].insert_one(data)
            results['MongoDB'] = f"Document inserted with ID: {str(result.inserted_id)}"

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. Update Data
@app.route('/update_data', methods=['PUT'])
def update_data():
    try:
        database = request.args.get('database')
        table = request.json['table']
        data = request.json['data']

        results = {}

        if database in ['postgres', 'both']:
            pg_conn = connect_postgres()
            with pg_conn.cursor() as cur:
                updates = []
                params = []

                if table == 'Users':
                    if data.get('name') is not None:
                        updates.append("name = %s")
                        params.append(data['name'])
                    if data.get('email') is not None:
                        updates.append("email = %s")
                        params.append(data['email'])
                    if data.get('region') is not None:
                        updates.append("region = %s")
                        params.append(data['region'])
                    params.append(data['user_id'])
                    query = f"UPDATE Users SET {', '.join(updates)} WHERE user_id = %s"

                elif table == 'Videos':
                    if data.get('title') is not None:
                        updates.append("title = %s")
                        params.append(data['title'])
                    if data.get('description') is not None:
                        updates.append("description = %s")
                        params.append(data['description'])
                    if data.get('upload_date') is not None:
                        updates.append("upload_date = %s")
                        params.append(data['upload_date'])
                    if data.get('category') is not None:
                        updates.append("category = %s")
                        params.append(data['category'])
                    params.append(data['video_id'])
                    query = f"UPDATE Videos SET {', '.join(updates)} WHERE video_id = %s"

                cur.execute(query, params)
                pg_conn.commit()
            pg_conn.close()
            results['PostgreSQL'] = "Update successful"

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. Delete Data
@app.route('/delete_data', methods=['DELETE'])
def delete_data():
    try:
        database = request.args.get('database')
        table = request.json['table']
        data = request.json['data']

        results = {}

        if database in ['postgres', 'both']:
            pg_conn = connect_postgres()
            with pg_conn.cursor() as cur:
                if table == 'Users':
                    cur.execute("DELETE FROM Users WHERE user_id = %s", (data['user_id'],))
                elif table == 'Videos':
                    cur.execute("DELETE FROM Videos WHERE video_id = %s", (data['video_id'],))
                pg_conn.commit()
            pg_conn.close()
            results['PostgreSQL'] = "Delete successful"

        if database in ['mongo', 'both']:
            mongo_db = connect_mongo()
            mongo_collection = mongo_db[table]
            from bson.objectid import ObjectId
            mongo_collection.delete_one({"_id": ObjectId(data['_id'])})
            results['MongoDB'] = "Delete successful"

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    try:
        database = request.args.get('database')
        table = request.json['table']
        data = request.json['data']

        results = {}

        if database in ['postgres', 'both']:
            pg_conn = connect_postgres()
            with pg_conn.cursor() as cur:
                if table == 'Users':
                    cur.execute("DELETE FROM Users WHERE user_id = %s", (data['user_id'],))
                elif table == 'Videos':
                    cur.execute("DELETE FROM Videos WHERE video_id = %s", (data['video_id'],))
                pg_conn.commit()
            pg_conn.close()
            results['PostgreSQL'] = "Delete successful"

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve the Frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

# Main App
if __name__ == '__main__':
    app.run(debug=True)
