from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import signal
from threading import Thread, Event

from core.analytics_engine_thread import AnalyticsEngineThread
from calculators.price_calculator import PriceCalculator
from calculators.returns_calculator import ReturnsCalculator
from core.analytics_engine import AnalyticsEngine
from core.symbol_store import SymbolStore
from utils.logger import Logger
from network.lunar_crush_client import LunarCrushClient

engine_thread = Thread()
engine_thread_stop_event = Event()


def sigint_handler(signum, frame):
    logger.log("Catching CTRL C signal.")

    engine_thread_stop_event.set()
    exit()


signal.signal(signal.SIGINT, sigint_handler)

# In Heroku deployment environment, `__name__` will be set to `main`.
is_production = __name__ == "main"

logger = Logger.get_instance()

symbol_store = SymbolStore.get_instance()
lunar_crush_client = LunarCrushClient(symbol_store)
calculators = [PriceCalculator(), ReturnsCalculator()]
analytics_engine = AnalyticsEngine(lunar_crush_client, symbol_store, calculators)


app = Flask(__name__)
socket_io = SocketIO(app)


@app.route("/")
def index():
    logger.log(
        "Handling request to root URI by returning the WebSockets service HTML page."
    )

    return render_template("/index.html")


@app.route("/analytics")
def analytics():
    logger.log("Handling request to root URI by returning analytics cache dictionary.")

    return analytics_engine.output


@socket_io.on("my_event")
def test_message(message):
    emit("my response", {"data": "got it!"})


@socket_io.on("register")
def register(message):
    global engine_thread
    logger.log("Client connecting to Coinarius WebSocket service")

    # Start the engine thread only if it has not been started before.
    if not engine_thread.is_alive():
        logger.log("Starting Analytics Engine Thread.")
        engine_thread = AnalyticsEngineThread(
            socket_io, analytics_engine, engine_thread_stop_event
        )
        engine_thread.start()


@socket_io.on("unregister", namespace="/user")
def unregister():
    # TODO
    global engine_thread
    logger.log("Client disconnecting from Coinarius WebSocket service")


if __name__ == "__main__":
    logger.log("Starting Coinarius Analytics!")
    analytics_engine.initialise()

    logger.log("Starting Flask/SocketIO server!")
    socket_io.run(app, debug=True, use_reloader=False)
