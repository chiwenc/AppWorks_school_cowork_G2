from server import app
from waitress import serve

if __name__ == "__main__":
    app.run('0.0.0.0',port=3000)
    # serve(app, host='0.0.0.0', port=3000)