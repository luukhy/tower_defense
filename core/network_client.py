import json
import socket

from PyQt6.QtCore import QThread, pyqtSignal


class NetworkClient(QThread):
    connected_signal = pyqtSignal()
    disconnected_signal = pyqtSignal()
    message_received_signal = pyqtSignal(dict)

    def __init__(self, host="127.0.0.1", port=5555, player_id="Player_1"):
        super().__init__()
        self.host = host
        self.port = port
        self.player_id = player_id

        self.client_socket = None
        self.is_running = False

    def run(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.is_running = True

            login_data = {"action": "LOGIN", "id": self.player_id}
            self.send_message(login_data)

            self.connected_signal.emit()
            print("Connected to server")

            with self.client_socket.makefile("r") as reader:
                while self.is_running:
                    line = reader.readline()
                    if not line:
                        break

                    try:
                        data = json.loads(line.strip())
                        self.message_received_signal.emit(data)
                    except json.JSONDecodeError:
                        print("Received corrupted JSON")

        except Exception as e:
            print(f"Network error: {e}")

        finally:
            self.is_running = False
            if self.client_socket:
                self.client_socket.close()
            self.disconnected_signal.emit()

    def send_message(self, data_dict: dict):
        if self.is_running and self.client_socket:
            try:
                data_dict["id"] = self.player_id
                json_string = json.dumps(data_dict) + "\n"
                self.client_socket.sendall(json_string.encode())
            except Exception as e:
                print(f"Failed to send message: {e}")

    def stop(self):
        self.is_running = False
        if self.client_socket:
            self.client_socket.close()
