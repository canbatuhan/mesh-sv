import socket
import json

FORMAT = "utf-8"

class UDPHandler:
    def __init__(self) -> None:
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.bind(("127.0.0.1", 0))

    def send(self, req:dict, dest_addr:tuple[str, int]) -> None:
        decoded_req = json.dumps(req).encode(FORMAT)
        self.__socket.sendto(decoded_req, dest_addr)

    def recv(self, buffer_size:int) -> tuple[dict, tuple[str, int]]:
        raw_data, source_addrs = self.__socket.recvfrom(buffer_size)
        data = json.loads(raw_data.decode(FORMAT))
        return data, source_addrs

    def get_addrs(self) -> tuple[str, int]:
        addrs = self.__socket.getsockname()
        return addrs[0], addrs[1]