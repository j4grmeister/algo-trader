import alpaca
import json

symbol_listeners = {}
global_listeners = []

def register_symbol_listener(symbol, thread):
    if symbol not in symbol_listeners:
        symbol_listeners[symbol] = []
    symbol_listeners[symbol].append(thread)

def register_global_listener(thread):
    global_listeners.append(thread)

@alpaca.alpaca_socket.open_listener
def on_open(ws):
    pass
    
@alpaca.alpaca_socket.message_listener
def on_message(ws, message):
    message_json = json.loads(message)
    for row in message_json:
        if 'S' in row:
            # notify global listeners
            for thread in global_listeners:
                thread.notify(row)
            # notify any registered listeners
            if row['S'] in symbol_listeners:
                for thread in symbol_listeners[row['S']]:
                    thread.notify(row)

@alpaca.alpaca_socket.error_listener
def on_error(ws, error):
    print(json.loads(error))

@alpaca.alpaca_socket.close_listener
def on_close(ws):
    pass # TODO: reconnect to socket