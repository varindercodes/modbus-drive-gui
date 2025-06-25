# This script creates a simple GUI to control a drive using Modbus TCP.
# Written with Python GTK (PyGObject) and modbus-tk.

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from modbus_tk import modbus_tcp
from modbus_tk import defines as cst

# -------------------------------
# Modbus and Drive Configuration
# -------------------------------
MODBUS_IP = "127.0.0.1"  # Change this to your Modbus slave's IP
MODBUS_PORT = 502        # Default Modbus TCP port
SLAVE_ID = 1             # Modbus slave ID (depends on your device)
START_ADDRESS = 0        # Starting register address
BLOCK_TYPE = cst.HOLDING_REGISTERS

# -------------------------------
# Main GTK Application Class
# -------------------------------
class DriveControlUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Drive Control Panel")
        self.set_border_width(15)
        self.set_default_size(350, 300)

        # These are the labels that describe what each bit means
        self.labels = [
            "Coast (0=Run, 1=Stop)",
            "Regen Mode (0=Follow Speed Cmd, 1=Ignore)",
            "Direction (0=Forward, 1=Reverse)",
            "Tach Feedback (0=Voltage, 1=Tach)",
            "Motor Overload Protection (0=Off, 1=On)",
            "Torque Mode (0=Voltage, 1=Amperage)"
        ]

        # List to store the CheckButton widgets
        self.checkboxes = []

        # Layout container
        vbox = Gtk.VBox(spacing=10)

        # Create a checkbox row for each setting
        for label in self.labels:
            hbox = Gtk.HBox(spacing=10)
            lbl = Gtk.Label(label=label, xalign=0)
            checkbox = Gtk.CheckButton()
            hbox.pack_start(lbl, True, True, 0)
            hbox.pack_end(checkbox, False, False, 0)
            vbox.pack_start(hbox, False, False, 0)
            self.checkboxes.append(checkbox)

        # Add the Send button
        send_button = Gtk.Button(label="Send to Drive")
        send_button.connect("clicked", self.send_to_drive)
        vbox.pack_start(send_button, False, False, 20)

        # Final setup
        self.add(vbox)

    # Function that gathers checkbox values and sends them via Modbus
    def send_to_drive(self, button):
        values = [int(cb.get_active()) for cb in self.checkboxes]
        print("Sending:", values)

        try:
            # Connect to Modbus slave
            master = modbus_tcp.TcpMaster(host=MODBUS_IP, port=MODBUS_PORT)
            master.set_timeout(2.0)

            # Write multiple registers
            master.execute(
                slave=SLAVE_ID,
                function_code=cst.WRITE_MULTIPLE_REGISTERS,
                starting_address=START_ADDRESS,
                output_value=values
            )

            print("✔️ Command sent successfully.")

        except Exception as e:
            print("❌ Failed to send command:", e)

# -------------------------------
# Run the App
# -------------------------------
if __name__ == "__main__":
    app = DriveControlUI()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
