import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import modbus_tk.modbus_rtu as modbus_rtu
import modbus_tk.defines as cst
import serial

# --------- Configuration ----------
PORT = "COM3"   # Change to your serial port (/dev/ttyUSB0)
BAUD = 9600
SLAVE = 1

INPUT_COUNT = 6
COIL_COUNT = 6

INPUT_NAMES = [
    "Speed (rpm)",
    "Current (A)",
    "AC Voltage (V)",
    "Firmware version",
    "Command feedback",
    "Line frequency"
]

# --------- GUI Class --------------
class SimulatorStatus(Gtk.Window):
    def __init__(self):
        super().__init__(title="Simulator Status")
        self.set_border_width(10)
        self.set_default_size(350, 300)

        box = Gtk.VBox(spacing=8)

        # Labels for input registers
        self.input_labels = []
        for name in INPUT_NAMES:
            lbl = Gtk.Label(f"{name}: --", xalign=0)
            box.pack_start(lbl, False, False, 0)
            self.input_labels.append(lbl)

        # Label for coil values
        self.coil_label = Gtk.Label("Coils: --", xalign=0)
        box.pack_start(self.coil_label, False, False, 0)

        # Refresh button
        btn = Gtk.Button(label="Refresh Status")
        btn.connect("clicked", self.on_refresh)
        box.pack_start(btn, False, False, 10)

        self.add(box)
        self.setup_modbus()

    def setup_modbus(self):
        ser = serial.Serial(port=PORT, baudrate=BAUD, bytesize=8, parity='N', stopbits=1)
        self.master = modbus_rtu.RtuMaster(ser)
        self.master.set_timeout(2.0)
        self.master.set_verbose(False)

    def on_refresh(self, _):
        try:
            # Read 6 input registers
            regs = self.master.execute(SLAVE, cst.READ_INPUT_REGISTERS, 0, INPUT_COUNT)
            for i, val in enumerate(regs):
                self.input_labels[i].set_text(f"{INPUT_NAMES[i]}: {val}")

            # Read 6 coils
            coils = self.master.execute(SLAVE, cst.READ_COILS, 0, COIL_COUNT)
            self.coil_label.set_text("Coils: " + "".join(str(int(b)) for b in coils))

        except Exception as e:
            self.coil_label.set_text("Error: " + str(e))

# --------- Launch App -------------
if __name__ == "__main__":
    win = SimulatorStatus()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
