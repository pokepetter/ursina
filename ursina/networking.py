from ursina.vec2 import Vec2
from ursina.vec3 import Vec3
from ursina.vec4 import Vec4

import panda3d.core as p3d

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from collections import deque

import uuid
import hashlib

import types
import typing
import inspect

import socket
import ssl
import select
import errno

import struct

import time

import atexit
import signal

class TCPPacketConnection:
    def __init__(self, socket, address, connection_timeout=None):
        self.socket = socket
        self.address = address
        self.connection_timeout = connection_timeout

        self.connected = True
        
        self.received_bytes_once = False
        self.last_time_bytes_received = 0.0
        self.time_since_bytes_received = 0.0
        self.timed_out = False

        self.state = "l"
        self.length_byte_count = 4
        self.expected_byte_count = self.length_byte_count
        self.bytes_received = bytearray()
        self.packet_queue = deque()

        self.buffer = bytearray()

    def __hash__(self):
        return hash(self.address)

    def __eq__(self, other):
        return self.address == other.address
    
    def receive(self):
        if not self.connected:
            return

        if self.socket.fileno() == -1:
            self.connected = False
            return

        b = None
        try:
            b = self.socket.recv(self.expected_byte_count)
        except socket.error as e:
            pass

        now = time.time()
        if self.received_bytes_once:
            self.time_since_bytes_received = now - self.last_time_bytes_received
            if b is not None:
                self.last_time_bytes_received = now
        else:
            self.last_time_bytes_received = now
        if self.connection_timeout is not None:
            if self.time_since_bytes_received >= self.connection_timeout:
                self.connected = False
                self.timed_out = True
                return
        self.received_bytes_once = True

        if b is None:
            return

        if len(b) == 0:
            self.connected = False
            return

        self.bytes_received += b
        self.expected_byte_count -= len(b)

        if self.expected_byte_count == 0:
            if self.state == "l":
                l = struct.unpack(">I", self.bytes_received)[0]
                self.state = "c"
                self.expected_byte_count = l
                self.bytes_received.clear()
            elif self.state == "c":
                self.packet_queue.append(self.bytes_received.copy())
                self.state = "l"
                self.expected_byte_count = self.length_byte_count
                self.bytes_received.clear()

    def has_packet(self):
        return len(self.packet_queue) > 0

    def next_packet(self):
        return bytes(self.packet_queue.popleft())

    def clear_buffer(self):
        self.buffer.clear()

    def write_to_buffer(self, byte_data):
        self.buffer += byte_data

    def get_buffer_length(self):
        return len(self.buffer)

    def send_buffer(self):
        try:
            self.socket.send(self.buffer)
            self.buffer.clear()
        except:
            self.connected = False

    def send(self, bytes_data):
        if not self.connected:
            return

        b = bytearray()
        b += struct.pack(">I", len(bytes_data))
        b += bytes_data

        try:
            self.socket.send(b)
        except:
            self.connected = False

    def disconnect(self):
        if not self.connected:
            return

        try:
            self.socket.close()
        except:
            pass
        self.connected = False

    def reconnect(self):
        if self.connected:
            return

        try:
            self.socket.connect(self.address)
            self.connected = True
            self.received_bytes_once = False
            self.last_time_bytes_received = 0.0
            self.time_since_bytes_received = 0.0
            self.timed_out = False
        except:
            pass

    def is_timed_out(self):
        return self.timed_out

    def is_connected(self):
        return self.connected


class TCPPacketServer:
    def __init__(self, on_connect=None, on_disconnect=None, on_data=None, on_raw_data=None, connection_timeout=None, path_to_certchain=None, path_to_private_key=None):
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_data = on_data
        self.on_raw_data = on_raw_data
        self.connection_timeout = connection_timeout
        self.path_to_certchain = path_to_certchain
        self.path_to_private_key = path_to_private_key

        self.use_tls = False
        if self.path_to_certchain is not None and self.path_to_private_key is not None:
            self.use_tls = True

        self.ssl_context = None
        if self.use_tls:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_context.load_cert_chain(self.path_to_certchain, self.path_to_private_key)

        self.connections = []

        self.socket = None
        self.secure_socket = None
        self.host_name = None
        self.port = None
        self.running = False

        def on_application_exit():
            if self.running:
                self.stop()

        atexit.register(on_application_exit)

        prev_signal_handler = signal.getsignal(signal.SIGINT)

        def on_keyboard_interrupt(*args):
            if self.running:
                self.stop()
            if prev_signal_handler is not None:
                if prev_signal_handler != signal.SIG_DFL:
                    prev_signal_handler(*args)

        signal.signal(signal.SIGINT, on_keyboard_interrupt)

    def start(self, host_name, port, backlog=100):
        assert not self.running, "Can't start TCP server that is already running."

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host_name, port))
        self.socket.listen(backlog)
        self.socket.setblocking(False)
        if self.use_tls:
            self.secure_socket = self.ssl_context.wrap_socket(self.socket, server_side=True)
        self.host_name = host_name
        self.port = port
        self.running = True

    def stop(self):
        assert self.running, "Can't stop TCP server that is not running."

        try:
            self.disconnect_all()
            if self.use_tls:
                self.secure_socket.close()
            self.socket.close()
        except:
            pass

        self.running = False

    def update(self, max_packets=100):
        assert self.running, "Can't update TCP server that is not running."
        
        server_socket = self.socket
        if self.use_tls:
            server_socket = self.secure_socket

        try:
            client_socket, client_address = server_socket.accept()
            client_socket.setblocking(False)
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            connection = TCPPacketConnection(client_socket, client_address, connection_timeout=self.connection_timeout)
            self.connections.append(connection)
            if self.on_connect is not None:
                self.on_connect(connection)
        except:
            pass

        packet_count = 0
        for connection in self.connections:
            connection.receive()
            while connection.has_packet() and packet_count < max_packets:
                packet = connection.next_packet()
                if self.on_data is not None:
                    # Allow for middleware handler that intercepts data.
                    if self.on_raw_data is not None:
                        r = self.on_raw_data(connection, packet)
                        self.on_data(connection, r)
                    else:
                        self.on_data(connection, packet)
                packet_count += 1
            if connection.get_buffer_length() > 0:
                connection.send_buffer()

        to_be_removed = []
        for connection in self.connections:
            if not connection.is_connected():
                to_be_removed.append(connection)
        for connection in to_be_removed:
            if self.on_disconnect is not None:
                self.on_disconnect(connection)
            self.connections.remove(connection)

    def disconnect_all(self):
        to_be_removed = []
        for connection in self.connections:
            to_be_removed.append(connection)
        for connection in to_be_removed:
            connection.disconnect()
            if self.on_disconnect is not None:
                self.on_disconnect(connection)
            self.connections.remove(connection)

    def is_running(self):
        return self.running


class TCPPacketClient:
    def __init__(self, on_connect=None, on_disconnect=None, on_data=None, on_raw_data=None, connection_timeout=None, use_tls=False, path_to_cabundle=None):
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_data = on_data
        self.on_raw_data = on_raw_data
        self.connection_timeout = connection_timeout
        self.use_tls = use_tls
        self.path_to_cabundle = path_to_cabundle

        self.ssl_context = None
        if self.use_tls:
            if path_to_cabundle is not None:
                self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                self.ssl_context.load_verify_locations(self.path_to_cabundle)
            else:
                self.ssl_context = ssl.create_default_context()

        self.connection = None

        self.socket = None
        self.secure_socket = None
        self.host_name = None
        self.port = None
        self.running = False

        def on_application_exit():
            if self.running:
                self.stop()

        atexit.register(on_application_exit)

        prev_signal_handler = signal.getsignal(signal.SIGINT)

        def on_keyboard_interrupt(*args):
            if self.running:
                self.stop()
            if prev_signal_handler is not None:
                if prev_signal_handler != signal.SIG_DFL:
                    prev_signal_handler(*args)

        signal.signal(signal.SIGINT, on_keyboard_interrupt)

    def start(self, host_name, port, tls_host_name=None):
        assert not self.running, "Can't start TCP client that is already running."

        if tls_host_name is None:
            tls_host_name = host_name

        try:
            self.socket = socket.create_connection((host_name, port))
            client_socket = self.socket
            if self.use_tls:
                try:
                    self.secure_socket = self.ssl_context.wrap_socket(self.socket, server_hostname=tls_host_name)
                    self.secure_socket.setblocking(False)
                    client_socket = self.secure_socket
                except Exception as e:
                    print(e)
                    raise e
            else:
                self.socket.setblocking(False)
            self.host_name = host_name
            self.port = port
            self.running = True
            self.connection = TCPPacketConnection(client_socket, (host_name, port), connection_timeout=self.connection_timeout)
            if self.on_connect is not None:
                self.on_connect(self.connection)
        except:
            return False

        return True

    def stop(self):
        assert self.running, "Can't stop TCP client that is not running."

        try:
            self.socket.close()
            if self.on_disconnect is not None:
                self.on_disconnect(self.connection)
        except:
            pass

        self.running = False

    def update(self, max_packets=100):
        assert self.running, "Can't update TCP client that is not running."
        
        client_socket = self.socket
        if self.use_tls:
            client_socket = self.secure_socket

        self.connection.receive()
        packet_count = 0
        while self.connection.has_packet() and packet_count < max_packets:
            packet = self.connection.next_packet()
            if self.on_data is not None:
                # Allow for middleware handler that intercepts data.
                if self.on_raw_data is not None:
                    r = self.on_raw_data(self.connection, packet)
                    self.on_data(self.connection, r)
                else:
                    self.on_data(self.connection, packet)
            packet_count += 1
        if self.connection.get_buffer_length() > 0:
            self.connection.send_buffer()

        if not self.connection.is_connected():
            self.stop()

    def send(self, bytes_data):
        self.connection.send(bytes_data)

    def is_running(self):
        return self.running


class DatagramWriter:
    def __init__(self):
        self.datagram = PyDatagram()

    def get_datagram(self):
        return self.datagram

    def write(self, value):
        if isinstance(value, bool):
            self.write_int8(int(value))
        elif isinstance(value, int):
            self.write_int64(value)
        elif isinstance(value, float):
            self.write_float64(value)
        elif isinstance(value, str):
            self.write_string32(value)
        elif isinstance(value, p3d.Vec2):
            self.write_float64(value[0])
            self.write_float64(value[1])
        elif isinstance(value, p3d.Vec3):
            self.write_float64(value[0])
            self.write_float64(value[1])
            self.write_float64(value[2])
        elif isinstance(value, p3d.Vec4):
            self.write_float64(value[0])
            self.write_float64(value[1])
            self.write_float64(value[2])
            self.write_float64(value[3])
        elif isinstance(value, tuple):
            for v in value:
                self.write(v)
        elif isinstance(value, list):
            self.write_int32(len(value))
            for v in value:
                self.write(v)
        else:
            raise Exception("Unspported value type for DatagramWriter: {0}".format(type(value).__name__))

    def write_string(self, value):
        self.datagram.addString(value)

    def write_string32(self, value):
        self.datagram.addString32(value)

    def write_int8(self, value):
        self.datagram.addBeInt8(value)

    def write_int16(self, value):
        self.datagram.addBeInt16(value)

    def write_int32(self, value):
        self.datagram.addBeInt32(value)

    def write_int64(self, value):
        self.datagram.addBeInt64(value)

    def write_float32(self, value):
        self.datagram.addBeFloat32(value)

    def write_float64(self, value):
        self.datagram.addBeFloat64(value)

    def write_blob(self, value):
        self.datagram.addBlob(value)

    def write_blob32(self, value):
        self.datagram.addBlob32(value)


class DatagramReader:
    def __init__(self, datagram):
        self.datagram = datagram
        self.iter = PyDatagramIterator(self.datagram)

    def get_datagram(self):
        return self.datagram

    def read(self, value_type, max_list_length=1000):
        if value_type is bool:
            return bool(self.read_int8())
        elif value_type is int:
            return self.read_int64()
        elif value_type is float:
            return self.read_float64()
        elif value_type is str:
            return self.read_string32()
        elif value_type is Vec2:
            return Vec2(self.read_float64(), self.read_float64())
        elif value_type is Vec3:
            return Vec3(self.read_float64(), self.read_float64(), self.read_float64())
        elif value_type is Vec4:
            return Vec4(self.read_float64(), self.read_float64(), self.read_float64(), self.read_float64())
        elif value_type is types.GenericAlias:
            origin_type = tpying.get_origin(value_type)
            if origin_type is tuple:
                arg_types = typing.get_args(value_type)
                values = []
                for arg_type in arg_types:
                    values.append(self.read(arg_type))
                return tuple(values)
            elif origin_type is list:
                arg_type = typing.get_args(value_type)[0]
                if arg_type is list:
                    raise Exception("DatagramReader does not support lists of lists.")
                l = self.read_int32()
                if l > max_list_length:
                    raise Exception("Received list that exceeds the max list length allowed by the DatagramReader.")
                values = []
                for i in range(l):
                    values.append(self.read(arg_type))
                return values
        else:
            raise Exception("Unspported value type for DatagramReader: {0}".format(value_type.__name__))

    def read_string(self):
        return self.iter.getString()

    def read_string32(self):
        return self.iter.getString32()

    def read_int8(self):
        return self.iter.getBeInt8()

    def read_int16(self):
        return self.iter.getBeInt16()

    def read_int32(self):
        return self.iter.getBeInt32()

    def read_int64(self):
        return self.iter.getBeInt64()

    def read_float32(self):
        return self.iter.getBeFloat32()

    def read_float64(self):
        return self.iter.getBeFloat64()

    def read_blob(self):
        return self.iter.getBlob()

    def read_blob32(self):
        return self.iter.getBlob32()
    

# Gives a 32 bit hash value (shifted one right (31 bit)) that is the same across runs and devices.
def procedure_hash(name):
    h = hashlib.sha1(name.encode("utf-8")).digest()
    return int.from_bytes(h[:4], byteorder="big") >> 1


class RPCServer:
    def __init__(self, max_list_length=16, **kwargs):
        self.server = TCPPacketServer(**kwargs)

        self.max_list_length = max_list_length

        def default_on_connect(connection):
            print("New connection:", connection.address)

        def default_on_disconnect(connection):
            print("Disconnected:", connection.address)

        def on_data(connection, data):
            self.rpc_on_data(connection, data)

        if self.server.on_connect is None:
            self.server.on_connect = default_on_connect
        if self.server.on_disconnect is None:
            self.server.on_disconnect = default_on_disconnect
        self.server.on_data = on_data

        self.procedures = dict()

    def start(self, host_name, port, backlog=100):
        return self.server.start(host_name, port, backlog=backlog)

    def stop(self):
        self.server.stop(*args, **kwargs)

    def update(self):
        self.server.update()

    def is_running(self):
        return self.server.is_running()

    def disconnect_all(self):
        self.server.disconnect_all()

    def register_procedure(self, proc):
        func_spec = inspect.getfullargspec(proc)
        arg_types = []
        for func_arg in func_spec.args[1:]:
            func_arg_type = func_spec.annotations.get(func_arg)
            if func_arg_type is None:
                raise Exception("RCPServer failed to register the '{}' procedure, it's missing one or more type annotations for the arguments.".format(proc.__name__))
            arg_types.append(func_arg_type)
        procedure_name_hash = procedure_hash(proc.__name__)
        self.procedures[procedure_name_hash] = (proc.__name__, arg_types, proc)

    def __getattr__(self, name):
        def remote_procedure(*args):
            assert len(args) >= 1, "RPC must have at least one argument. The connection."
            assert isinstance(args[0], TCPPacketConnection), "First argument to RPC must be a TCPPacketConnection."
            writer = DatagramWriter()
            procedure_name_hash = procedure_hash(name)
            writer.write_int32(procedure_name_hash)
            connection = args[0]
            for arg in args[1:]:
                writer.write(arg)
            connection.send(writer.get_datagram().getMessage())

        return remote_procedure

    def rpc_on_data(self, connection, data):
        reader = DatagramReader(p3d.Datagram(data))
        proc_name = None
        proc_func = None
        proc_arg_values = None
        try:
            procedure_name_hash = reader.read_int32()
            proc = self.procedures.get(procedure_name_hash)
            if proc is None:
                raise Exception("Server procedure does not exist.")
            proc_name = proc[0]
            proc_arg_types = proc[1]
            proc_func = proc[2]
            proc_arg_values = []
            for t in proc_arg_types:
                v = reader.read(t, max_list_length=self.max_list_length)
                proc_arg_values.append(v)
        except:
            connection.disconnect()

        if proc_func is not None and proc_arg_values is not None:
            proc_func(connection, *proc_arg_values)


class RPCClient(TCPPacketClient):
    def __init__(self, max_list_length=16, **kwargs):
        self.client = TCPPacketClient(**kwargs)

        self.max_list_length = max_list_length

        def default_on_connect(connection):
            print("New connection:", connection.address)

        def default_on_disconnect(connection):
            print("Disconnect:", connection.address)

        def on_data(connection, data):
            self.rpc_on_data(connection, data)

        if self.client.on_connect is None:
            self.client.on_connect = default_on_connect
        if self.client.on_disconnect is None:
            self.client.on_disconnect = default_on_disconnect
        self.client.on_data = on_data

        self.procedures = dict()

    def start(self, host_name, port, tls_host_name=None):
        return self.client.start(host_name, port, tls_host_name=tls_host_name)

    def stop(self):
        self.client.stop()

    def update(self):
        self.client.update()

    def is_running(self):
        return self.client.is_running()

    def register_procedure(self, proc):
        func_spec = inspect.getfullargspec(proc)
        arg_types = []
        for func_arg in func_spec.args[1:]:
            func_arg_type = func_spec.annotations.get(func_arg)
            if func_arg_type is None:
                raise Exception("RCPClient failed to register the '{}' procedure, it's missing one or more type annotations for the arguments.".format(proc.__name__))
            arg_types.append(func_arg_type)
        procedure_name_hash = procedure_hash(proc.__name__)
        self.procedures[procedure_name_hash] = (proc.__name__, arg_types, proc)

    def __getattr__(self, name):
        def remote_procedure(*args):
            writer = DatagramWriter()
            procedure_name_hash = procedure_hash(name)
            writer.write_int32(procedure_name_hash)
            for arg in args:
                writer.write(arg)
            self.client.send(writer.get_datagram().getMessage())

        return remote_procedure

    def rpc_on_data(self, connection, data):
        reader = DatagramReader(p3d.Datagram(data))
        try:
            procedure_name_hash = reader.read_int32()
            proc = self.procedures.get(procedure_name_hash)
            if proc is None:
                raise Exception("Client procedure does not exist.")
            proc_name = proc[0]
            proc_arg_types = proc[1]
            proc_func = proc[2]
            proc_arg_values = []
            for t in proc_arg_types:
                v = reader.read(t, max_list_length=self.max_list_length)
                proc_arg_values.append(v)
            proc_func(connection, *proc_arg_values)
        except:
            connection.disconnect()


# Convenience attribute applied to functions to register them as remote procedure calls.
#
# @rpc(my_rpc_server_object)
# def foo(x: int):
#     print(x)
def rpc(peer):
    def wrapper(f):
        peer.register_procedure(f)
    return wrapper


# Prevent error message spam from Panda3D network module.
p3d.loadPrcFileData("", "notify-level-net fatal")
