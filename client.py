import datetime
import random
import socket
from util import *

FORMAT = "utf-8"

class Client:
    def __init__(self) -> None:
        self.__servers = list[tuple[str, int]]()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def __log(self, msg) -> None:
        print("[CLIENT] {} - {}".format(
			datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S.%f"), msg))

    def take_request(self) -> None:
        raw_request = input("Enter Request: ")
        if raw_request.lower() == "exit": # Termninate command
            self.__log("Terminated")
            return raw_request.upper() # EXIT

        request_arr = raw_request.split(" ")
        command, _ = get_cmd_query(request_arr[0])

        if len(request_arr) == 2: # LOAD
            return generate_request(
                command, request_arr[1])
        elif len(request_arr) == 3: # STORE or UPDATE
            return generate_request(
                command, request_arr[1], int(request_arr[2]))
        
        else: # Invalid command
            self.__log("Invalid request")
            None

    def send_randomly(self, request:dict) -> None:
        with open(ADDRS_LIST_PATH, "r") as file:
            self.__servers.clear()
            for addr in file:
                host, port = addr.removesuffix("\n").split(":")
                self.__servers.append((host, int(port)))
        server = random.choice(self.__servers)
        self.__socket.sendto(json.dumps(request).encode(FORMAT), server)
        self.__log("REQ Sent: {} to {}:{}".format(
            request, server[0], server[1]))

    def receive_ack(self) -> None:
        ack, addr = self.__socket.recvfrom(BUFFER_SIZE)
        self.__log("ACK Received: {} from {}:{}".format(
            json.loads(ack), addr[0], addr[1]))


if __name__ == "__main__":
    client = Client()
    while True:
        request = client.take_request()
        if request == "EXIT": break
        elif request == None: continue

        client.send_randomly(request)
        client.receive_ack()