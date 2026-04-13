import asyncio
import json


class TCPServer:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 5555

        self.clients = {}

    async def broadcast(self, message: str, sender_name: str):
        if not message.endswith("\n"):
            message += "\n"

        encoded_msg = message.encode()

        for name, writer in self.clients.items():
            if name != sender_name:
                writer.write(encoded_msg)
                await writer.drain()

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):

        client_name = "Unknown"

        try:
            init_data = await reader.readline()
            if not init_data:
                return

            init_msg = json.loads(init_data.decode().strip())
            client_name = init_msg.get("id", f"Guest_{id(writer)}")

            self.clients[client_name] = writer
            print(f"{client_name} joined the game! Total players: {len(self.clients)}")

            while True:
                data = await reader.readline()
                if not data:
                    break

                message = data.decode()
                print(f"[{client_name}] {message.strip()}")

                await self.broadcast(message, sender_name=client_name)

        except Exception as e:
            print(f"Error with {client_name}: {e}")

        finally:
            print(f"{client_name} disconnected.")
            if client_name in self.clients:
                del self.clients[client_name]
            writer.close()
            await writer.wait_closed()

    async def start(self):
        """Starts the server and listens for new connections."""
        server = await asyncio.start_server(self.handle_client, self.host, self.port)

        print(f"Server started on {self.host}:{self.port}")

        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    server = TCPServer()

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nServer shut down manually.")
