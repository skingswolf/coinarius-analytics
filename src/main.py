from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Coinarius Analytics!"


if __name__ == "__main__":
    # Start the flask server.
    app.run()
