import datetime
import random
from smpai import FiniteStateMachine
from components.udp import UDPHandler
from util import *

class Server:
	def __init__(self) -> None:
		self.__udp_handler = UDPHandler() # UDP communcation class
		self.__statemachine = FiniteStateMachine(STATEMACHINE_PATH) # State Machine
		self.__statemachine.start()

	def __log(self, msg) -> None:
		print("[SERVER({})] {} - {}".format(
			self.__udp_handler.get_addrs()[1],
			datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S.%f"), msg))

	def listen(self) -> tuple[dict, tuple[str, int]]:
		request, src_addr = self.__udp_handler.recv(BUFFER_SIZE)
		variables = self.__statemachine.get_context().get_variables()
		last_req_id = variables.get("last_request").get("id")
		last_req_cmd = variables.get("last_request").get("cmd")

		if request.get("id") == last_req_id and request.get("cmd") == last_req_cmd: return None, None
		else: return request, src_addr

	def greet(self) -> None:
		self.__statemachine.send_event("START")
		with open(ADDRS_LIST_PATH, "a+") as file:
			file.seek(0)
			for neighbour_addr in file:
				# send GREET command
				host, port = neighbour_addr.removesuffix("\n").split(":")
				(command, _), dst_addr = get_cmd_query("GREET"), (host, int(port))				
				self.__udp_handler.send(generate_request(command), dst_addr)

				# receive GREET-ACK
				ack, greeting_addr = self.__udp_handler.recv(BUFFER_SIZE)
				greet_ack, _ = get_ack_nack("GREET")
				if ack == greet_ack:
					self.__statemachine.get_context().set_variable(
						"greeting_addr", {"host": greeting_addr[0], "port": greeting_addr[1]})
					self.__statemachine.send_event("GREET")
			
			# Add yourself into the shared file (server list)
			my_host, my_port = self.__udp_handler.get_addrs()
			my_addr_text = ":".join([my_host, str(my_port)])
			file.write(my_addr_text+"\n")

	def handle(self, request:dict, src_addr:tuple[str, int]) -> tuple[str, tuple[str, int]]:
		# Determine the request type
		# Client REQ ServerA = {"id": 1924, "cmd": "ST", "var_name": "v1", "var_size": 2048, "client_addr": None}
		# ServerA QUERY ServerB = {"id": 1924, "cmd": "ST?", "var_name": "v1", "var_size": 2048, "client_addr": None}
		# ServerA COMMIT ServerB = {"id": 1924, "cmd": "ST", "var_name": "v1", "var_size": 2048, "client_addr": ("192.168.1.42", 8080)}
				
		self.__statemachine.get_context().set_variable("last_request", request)
		self.__statemachine.get_context().set_variable("greeting_addr", {"host": src_addr[0], "port": src_addr[1]})
		cmd_query_name = get_cmd_query_name(request.get("cmd")) # Event to sent
		self.__statemachine.send_event(cmd_query_name)
		
		is_success = self.__statemachine.get_context().get_variable("is_success")
		if is_success: self.__statemachine.send_event("SUCCESS")
		else: self.__statemachine.send_event("FAIL")

		ack, nack = get_ack_nack(cmd_query_name)
		if "?" in request.get("cmd"): # ServerA QUERY ServerB,
			if is_success: return ack, src_addr # ServerB ACK ServerA 
			else: return nack, src_addr # ServerB NACK ServerA

		elif request.get("client_addr") is not None: # ServerA COMMIT ServerB
			client_addr = (request.get("client_addr").get("host"), request.get("client_addr").get("port"))
			if is_success: return ack, client_addr # ServerB ACK Client
			else: return nack, client_addr # ServerB NACK Client

		else: # Client REQ ServerA
			if is_success: return ack, src_addr # ServerA ACK Client
			else: return None, src_addr # Redirect REQUEST

	def query(self, request:dict) -> list[tuple[str, int]]:
		dst_addrs = list[tuple[str, int]]()
		request.update({"cmd": request.get("cmd")+"?"})
		neighbours = self.__statemachine.get_context().get_variable("neighbours")
		random.shuffle(neighbours)

		for neighbour_addr in neighbours:
			self.__udp_handler.send(request, (neighbour_addr.get("host"), neighbour_addr.get("port")))
			ack, src_addr = self.__udp_handler.recv(BUFFER_SIZE)
			if not is_nack(ack): dst_addrs.append(src_addr)
			if len(dst_addrs) >= 1: break

		return dst_addrs 

	def commit(self, request:dict, server_addrs:list[tuple[str, int]], dst_addr:tuple[str, int]) -> None:
		request.update({"cmd": request.get("cmd").removesuffix("?"), 
						"client_addr": {"host": dst_addr[0], "port": dst_addr[1]}})

		for server_addr in server_addrs:
			self.__udp_handler.send(request, server_addr)

	def send_ack(self, ack:str, dst_addr:tuple[str, int]) -> None:
		self.__udp_handler.send(ack, dst_addr)

	def leave(self) -> None:
		self.__statemachine.send_event("FINISH")
		neighbours = self.__statemachine.get_context().get_variable("neighbours")
		with open(ADDRS_LIST_PATH, "w") as file:
			for neighbour_addr in neighbours:
				# send LEAVE command
				command, _ = get_cmd_query("LEAVE")
				self.__udp_handler.send(command, (neighbour_addr.get("host"), neighbour_addr.get("port")))	

				# receive LEAVE-ACK
				_, _ = self.__udp_handler.recv(BUFFER_SIZE)
			
				# re-write server into the shared file (remove yourself at the end)
				addr_text = ":".join([neighbour_addr.get("host"), neighbour_addr.get("port")])
				file.write(addr_text+"\n")


if __name__ == "__main__":
	server = Server()
	server.greet()

	while True:
		try:
			request, src_addr = server.listen() # wait for the next message
			if request is None: continue # if already processed, skip

			ack, dst_addr = server.handle(request, src_addr) # try to handle the request

			if ack == None: # if not success, then query other servers
				server_addrs = server.query(request) # for the commands LOAD, STORE, UPDATE, REPLICATE
				if len(server_addrs) > 0: server.commit(request, server_addrs, dst_addr)
				else: server.send_ack("ABORT", dst_addr)
			
			else: # if success, then return ACK or NACK
				server.send_ack(ack, dst_addr) # return ACK

		except KeyboardInterrupt:
			break

	server.leave()