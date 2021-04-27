import os
import websocket
import json
from threading import Thread
import time

BASE_URL = os.environ['APCA_API_BASE_URL']
KEY_ID = os.environ['APCA_API_KEY_ID']
SECRET_KEY = os.environ['APCA_API_SECRET_KEY']
HEADERS = {'APCA-API-KEY-ID': KEY_ID, 'APCA-API-SECRET-KEY': SECRET_KEY}

class MarketSocket:
    def __init__(self):
        # websocket.enableTrace(True)
        self.connected = False
        self._open_listeners = []
        self._message_listeners = []
        self._error_listeners = []
        self._close_listeners = []
        self.ws = websocket.WebSocketApp(
            "wss://stream.data.alpaca.markets/v2/iex",
            on_open = self.on_open,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close
        )

    # listener decorators
    def open_listener(self, func):
        self._open_listeners.append(func)
        return func
    def message_listener(self, func):
        self._message_listeners.append(func)
        return func
    def error_listener(self, func):
        self._error_listeners.append(func)
        return func
    def close_listener(self, func):
        self._close_listeners.append(func)
        return func
    
    def on_open(self, ws):
        def attempt_connection(*args):
            # wait for an ack from the socket that a connection was established
            print("Waiting for acknowledgement from socket")
            self._ack_received = False
            while not (self._ack_received or self._connection_timeout):
                pass
            if self._connection_timeout:
                return
            print("Acknowwledgement received. Attempting authentication")
            ws.send(json.dumps({
                "action": "auth",
                "key": KEY_ID,
                "secret": SECRET_KEY
            }))
            self._ack_received = False
            while not (self._ack_received or self._connection_timeout):
                pass
            if self._connection_timeout:
                return
            print("Authentication succeeded. Secure connection has been established")
            print("----------------------------------------")
            self.connected = True
            # invoke open listeners
            for func in self._open_listeners:
                func(ws)
        connect_thread = Thread(target=attempt_connection)
        connect_thread.start()

    def on_message(self, ws, message):
        if not self.connected:
            # check if this message is a successful ack during the connect and authenticate process
            if json.loads(message)[0]['T'] == "success":
                self._ack_received = True
        else:
            for func in self._message_listeners:
                func(ws, message)

    def on_error(self, ws, error):
        if self.connected:
            for func in self._error_listeners:
                func(ws, error)

    def on_close(self, ws):
        print("Closing socket connection")
        if self.connected:
            for func in self._close_listeners:
                func(ws)
    
    # attempts to open a new connection
    # returns true if successful, false otherwise (if there is a timeout)
    def try_connection(self):
        def check_connection(*args):
            while(True):
                if self.connected or self._connection_timeout:
                    break
        print("----------------------------------------")
        print("Attempting secure connection with Alpaca socket")
        self._connection_timeout = False
        self.socket_thread = Thread(target=self.ws.run_forever)
        timeout_thread = Thread(target=check_connection)
        self.socket_thread.start()
        timeout_thread.start()
        timeout_thread.join(timeout=10)
        if not self.connected:
            print("Failed to establish secure connection. Timing out after 10 seconds")
            print("----------------------------------------")
            self._connection_timeout = True
            self.ws.close()
        return self.connected

# the active socket connection
# note that there may only be one active connection to the alpaca socket at any one time
alpaca_socket = MarketSocket()