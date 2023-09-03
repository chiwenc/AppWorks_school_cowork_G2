from server import app
from waitress import serve


if __name__ == "__main__":
    # if app.env == "production":
    #     serve(app, port=3000)
    # else:
        app.run("0.0.0.0", port=8000, debug=True)

    # run: waitress-serve --host 127.0.0.1 application:app
    # run: waitress-serve --host 0.0.0.0 application:app
