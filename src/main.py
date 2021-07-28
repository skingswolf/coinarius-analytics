from flask import Flask
import logging
from logging.config import dictConfig

from analytics_engine import AnalyticsEngine
from lunar_crush_client import LunarCrushClient

logger = logging.getLogger("coinarius_analytics")
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s - %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["wsgi"]},
    }
)

lunar_crush_client = LunarCrushClient()
analytics_engine = AnalyticsEngine(lunar_crush_client)

app = Flask(__name__)


@app.route("/")
def index():
    logging.info("Handling request to root URI by starting analytics engine.")

    return analytics_engine.start()


if __name__ == "__main__":
    logging.info("Starting Coinarius Analytics server!")

    # Start the flask server.
    app.run(debug=True)
