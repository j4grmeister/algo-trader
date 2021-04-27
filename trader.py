from threading import Thread
import json
import requests
import alpaca

symbol_threads = []

if __name__ == "__main__":
    print("------------------------------")
    print("Launching algo-trader v0.0")
    print("------------------------------")

    # retry connection until successful
    print("Attempting connection to Alpaca socket")
    while not alpaca.alpaca_socket.try_connection():
        print("Connection failed. Retrying...")

    # get the account's open positions
    # TODO: add a timeout
    response = requests.request(
        "GET",
        "{0}/v2/positions".format(alpaca.BASE_URL),
        headers=alpaca.HEADERS
    )
    global active_positions
    active_positions = response.json()

    # open symbol threads for all the positions
    for position in active_positions:
        print("Opening thread for position {0}".format(position["symbol"]))
        thread = alpaca.SymbolThread(
            symbol=position["symbol"],
            qty=position["qty"],
            avg_entry_price=position["avg_entry_price"]
        )
        thread.start()
        symbol_threads.append(thread)