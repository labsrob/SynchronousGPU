
from opcua import Client, ua
from opcua import ua

# Replace with your PLC's endpoint
url = "opc.tcp://192.168.100.100:4840"

# Create and connect client
client = Client(url)
client.connect()
print("Connected to OPC UA Server at", url)

# If the server requires credentials
# client.set_user("opcuser")
# client.set_password("opcpassword")
# client.connect()

# -- Browse the OPC UA Node Tree
root = client.get_root_node()
print("Root node is:", root)

# Browse children
objects = root.get_children()
for obj in objects:
    print(obj)

# myvar = client.get_node("ns=2;i=2")  # example NodeId
# mytag = client.get_node("ns=3;s=\"Motor.Speed\"")
# print("Motor speed =", mytag.get_value())
# value = myvar.get_value()
# print("PLC Value:", value)

# mytag.set_value(42)  # write integer

# def main():
#     # Create client instance
#     client = Client(url)
#
#     try:
#         logger.info(f"Connecting to OPC UA server at {SERVER_URL}...")
#         client.connect()
#         logger.info("Connected!")
#
#         # Get the node
#         node = client.get_node(NODE_ID)
#         logger.info(f"Accessing node: {NODE_ID}")
#
#         # Read current value
#         value = node.get_value()
#         logger.info(f"Current value: {value}")
#
#         # Write a new value (example: increment current value by 1)
#         new_value = value + 1
#         node.set_value(ua.Variant(new_value, ua.VariantType.Int32))
#         logger.info(f"New value written: {new_value}")
#
#     except Exception as e:
#         logger.error(f"An error occurred: {e}")
#
#     finally:
#         # Always disconnect properly
#         client.disconnect()
#         logger.info("Disconnected from server.")
#
# if __name__ == "__main__":
#     main()
