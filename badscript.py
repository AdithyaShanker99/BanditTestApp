from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    user_input = request.args.get('query')  # Directly getting user input from query parameters
    # Insecurely incorporating user input directly into SQL query
    query = f"SELECT * FROM products WHERE name LIKE '%{user_input}%'"
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return {'results': results}
    except Exception as e:
        return {'error': str(e)}
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
