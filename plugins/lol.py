# other_plugin.py

def on_load():
    print("Other Plugin Loaded!")

def on_message(client, message, clients):
    try:
        msg_str = message.decode('ascii').strip()
        
        # Check for a specific command or condition
        if msg_str == ".cum":
            client.send('lol'.encode(ascii))
    except Exception as e:
        print(f"An error occurred in the Other plugin: {e}")
