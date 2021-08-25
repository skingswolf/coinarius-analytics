from flask import Flask
from multiprocessing import Process, Manager

from calculators.price_calculator import PriceCalculator
from calculators.returns_calculator import ReturnsCalculator
from core.analytics_engine import AnalyticsEngine
from core.symbol_store import SymbolStore
from utils.logger import Logger
from network.lunar_crush_client import LunarCrushClient


logger = Logger.get_instance()

symbol_store = SymbolStore.get_instance()
lunar_crush_client = LunarCrushClient(symbol_store)
calculators = [PriceCalculator(), ReturnsCalculator()]
analytics_engine = AnalyticsEngine(lunar_crush_client, symbol_store, calculators)


app = Flask(__name__)

shared_state = None


@app.route("/")
def index():
    logger.log("Handling request to root URI by returning analytics cache dictionary.")
    num_updates = shared_state["update"]
    logger.log(f"Shared state has been updated {num_updates} times.")

    return shared_state["analytics"]


if __name__ == "__main__":
    logger.log("Starting Coinarius Analytics!")

    # Had to initialise engine within this if block to avoid the following process error:
    # "Attempt to start a new process before the current process has finished its bootstrapping phase."
    process_manager = Manager()
    shared_state = process_manager.dict()
    shared_state["analytics"] = None
    shared_state["update"] = 0

    analytics_engine.initialise(shared_state)

    engine_process = Process(target=analytics_engine.run, args=(shared_state,))
    engine_process.start()

    logger.log("Starting Flask server!")
    app.run(debug=True, use_reloader=False)

    engine_process.join()
