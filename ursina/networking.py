from ursina.vec2 import Vec2
from ursina.vec3 import Vec3
from ursina.vec4 import Vec4

import panda3d.core as p3d

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from enum import Enum, auto

from collections import deque
import queue

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

import threading
import asyncio

# Used internally by Peer.
class PeerEvent(Enum):
    ERROR = auto()
    CONNECT = auto()
    DISCONNECT = auto()
    DATA = auto()


# This class represents and single connection.
# It can be hashed and compared so that it may be used as a dictionary key.
# This is useful for mapping from a connection to player data.
class Connection:
    def __init__(self, peer, socket, address, connection_timeout):
        self.peer = peer
        self.socket = socket
        self.address = address

        self.connection_timeout = connection_timeout

        self.connected = True
        self.timed_out = False

        self.state = "l"
        self.length_byte_count = 2
        self.expected_byte_count = self.length_byte_count
        self.bytes_received = bytearray()

        self.uid = str(uuid.uuid4())

        self.receiving_thread = None

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        return self.uid == other.uid

    def send(self, data):
        b = bytearray()
        b += struct.pack(">H", len(data))
        b += data
        try:
            self.socket.sendall(b)
        except:
            pass

    def disconnect(self):
        if self.connected:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
            except:
                pass
            self.connected = False
            self.peer._remove_connection(self)

    def is_timed_out(self):
        return self.timed_out

    def is_connected(self):
        return self.connected

    def _receive(self):
        try:
            while True:
                data = None
                try:
                    if self.connection_timeout is not None:
                        self.socket.settimeout(self.connection_timeout)
                    data = self.socket.recv(self.expected_byte_count)
                except socket.timeout:
                    self.timed_out = True
                    raise
                except Exception as e:
                    raise
                if data is None:
                    break
                if len(data) == 0:
                    break
                self.bytes_received += data
                self.expected_byte_count -= len(data)

                if self.expected_byte_count == 0:
                    if self.state == "l":
                        l = struct.unpack(">H", self.bytes_received)[0]
                        self.state = "c"
                        self.expected_byte_count = l
                        self.bytes_received.clear()
                    elif self.state == "c":
                        d = bytes(self.bytes_received.copy())
                        self.peer.output_event_queue.put((PeerEvent.DATA, self, d, time.time()))
                        self.state = "l"
                        self.expected_byte_count = self.length_byte_count
                        self.bytes_received.clear()
        except:
            pass
        finally:
            self.disconnect()
            self.state = "l"
            self.bytes_received.clear()
            self.expected_byte_count = self.length_byte_count


# -- Description --
# The main driving class of the networking module.
# This is either a server or a client depending on if it's hosting or not.
# -- Callbacks --
# The arguments starting with "on" are callback functions for network events.
# Their arguments are generally (connection, data, time).
# The connect and disconnect functions don't have the data argument.
# See the networking samples or update function definition for more.
# -- TLS / secure networking --
# TLS support can be enabled with `use_tls=True`.
# The host requires the path to the certificate chain, and the private key.
# The client can make use of a given path to a certificate authority bundle for testing / development / self signed.
# -- Address family --
# The socket address family can be either "INET" (ipv4) or "INET6" (ipv6).
# -- Notes --
# Keep in mind that the networking in running on its own thread and you must therefore check if it's running (is_running).
class Peer:
    def __init__(self, on_connect=None, on_disconnect=None, on_data=None, on_raw_data=None,
                 connection_timeout=None,
                 use_tls=False,
                 path_to_certchain=None, path_to_private_key=None,
                 path_to_cabundle=None,
                 socket_address_family="INET"):
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.on_data = on_data
        self.on_raw_data = on_raw_data
        self.connection_timeout = connection_timeout
        self.use_tls = use_tls
        self.path_to_certchain = path_to_certchain
        self.path_to_private_key = path_to_private_key
        self.path_to_cabundle = path_to_cabundle
        if socket_address_family == "INET":
            self.socket_address_family = socket.AF_INET
        elif socket_address_family == "INET6":
            self.socket_address_family = socket.AF_INET6
        else:
            raise Exception("Invalid/unsupported socket address family '{socket_address_family}'.")

        self.ssl_context = None

        self.connections = []

        self.output_event_queue = queue.Queue()

        self.socket = None
        self.listen_socket = None
        self.host_name = None
        self.tls_host_name = None
        self.port = None
        self.backlog = 100
        self.is_host = False

        self.running = False

        self.main_thread = None
        self.server_listen_thread = None
        self.running_lock = threading.Lock()
        self.connections_lock = threading.Lock()

        def on_application_exit():
            if self.running:
                self.stop()

        atexit.register(on_application_exit)

        prev_signal_handler = signal.getsignal(signal.SIGINT)

        def on_keyboard_interrupt(*args):
            self.stop()
            if prev_signal_handler is not None:
                if prev_signal_handler != signal.SIG_DFL:
                    prev_signal_handler(*args)

        signal.signal(signal.SIGINT, on_keyboard_interrupt)

    def is_using_tls(self):
        return self.use_tls

    def start(self, host_name, port, is_host=False, backlog=100, tls_host_name=None, socket_address_family=None):
        if self.running:
            self.stop()

        if socket_address_family is not None:
            if socket_address_family == "INET":
                self.socket_address_family = socket.AF_INET
            elif socket_address_family == "INET6":
                self.socket_address_family = socket.AF_INET6
            else:
                raise Exception(f"Invalid/unsupported socket address family '{socket_address_family}'.")

        if is_host:
            if self.use_tls:
                self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                self.ssl_context.load_cert_chain(self.path_to_certchain, self.path_to_private_key)
        else:
            if self.use_tls:
                if self.path_to_cabundle is not None:
                    self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                    self.ssl_context.load_verify_locations(self.path_to_cabundle)
                else:
                    self.ssl_context = ssl.create_default_context()

        self.host_name = host_name
        self.tls_host_name = tls_host_name
        if self.tls_host_name is None and self.use_tls:
            self.tls_host_name = self.host_name
        self.port = port
        self.backlog = backlog
        self.is_host = is_host

        self.main_thread = threading.Thread(target=self._run, daemon=True)
        self.main_thread.start()

    def stop(self):
        if not self.running:
            return

        self.disconnect_all()

        with self.running_lock:
            self.running = False

        if self.is_host:
            try:
                self.listen_socket.shutdown(socket.SHUT_RDWR)
                self.listen_socket.close()
            except:
                raise

        self.main_thread.join()

        while not self.output_event_queue.empty():
            self.output_event_queue.get()

    def update(self, max_events=100):
        for i in range(max_events):
            if self.output_event_queue.empty():
                break
            next_event = self.output_event_queue.get()
            event_type = next_event[0]
            conn = next_event[1]
            d = next_event[2]
            t = next_event[3]
            if event_type == PeerEvent.CONNECT:
                if self.on_connect is not None:
                    self.on_connect(conn, t)
            elif event_type == PeerEvent.DISCONNECT:
                if self.on_disconnect is not None:
                    self.on_disconnect(conn, t)
            elif event_type == PeerEvent.DATA:
                if self.on_raw_data is not None:
                    d = self.on_raw_data(conn, d, t)
                if self.on_data is not None:
                    self.on_data(next_event[1], d, t)

    def send(self, connection, data):
        connection.send(data)

    def disconnect(self, connection):
        connection.disconnect()

    def disconnect_all(self):
        connections = self.get_connections()
        for connection in connections:
            connection.disconnect()

    def is_running(self):
        return self.running

    def is_hosting(self):
        return self.is_host

    def connection_count(self):
        return len(self.connections)

    def get_connections(self):
        connections_copy = None
        with self.connections_lock:
            connections_copy = self.connections.copy()
        return connections_copy

    def _add_connection(self, socket, address):
        connection = Connection(self, socket, address, self.connection_timeout)
        with self.connections_lock:
            self.connections.append(connection)
        self.output_event_queue.put((PeerEvent.CONNECT, connection, None, time.time()))
        connection.receiving_thread = threading.Thread(target=connection._receive, daemon=True)
        connection.receiving_thread.start()

    def _remove_connection(self, connection):
        with self.connections_lock:
            if connection in self.connections:
                self.connections.remove(connection)
                self.output_event_queue.put((PeerEvent.DISCONNECT, connection, None, time.time()))

    def _run_server(self):
        try:
            self.listen_socket = socket.socket(self.socket_address_family, socket.SOCK_STREAM, 0)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind((self.host_name, self.port))
            self.listen_socket.listen(self.backlog)
            if self.use_tls:
                self.listen_socket = self.ssl_context.wrap_socket(self.listen_socket, server_side=True)
        except Exception as e:
            print(e)
            raise

        with self.running_lock:
            self.running = True

        while self.running:
            try:
                client_socket, address = self.listen_socket.accept()
                client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            except:
                break
            self._add_connection(client_socket, address)

    def _run_client(self):
        client_socket = None
        if self.use_tls:
            try:
                self.socket = socket.socket(self.socket_address_family, socket.SOCK_STREAM, 0)
                client_socket = self.ssl_context.wrap_socket(self.socket, server_hostname=self.tls_host_name)
                client_socket.connect((self.host_name, self.port))
            except Exception as e:
                self.running = False
                return
        else:
            try:
                client_socket = socket.create_connection((self.host_name, self.port))
            except Exception as e:
                self.running = False
                return
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._add_connection(client_socket, (self.host_name, self.port))

        with self.running_lock:
            self.running = True

    def _run(self):
        if self.is_host:
            self._run_server()
        else:
            self._run_client()


# -- Description --
# Main serialization class used by the networking module.
class DatagramWriter:
    def __init__(self):
        self.datagram = PyDatagram()
        self.builtin_type_functions = {
            bool: self.write_bool,
            int: self.write_int64,
            float: self.write_float64,
            str: self.write_string32,
            Vec2: self.write_vec2,
            Vec3: self.write_vec3,
            Vec4: self.write_vec4,
            tuple: self.write_tuple,
            list: self.write_list,
            bytes: self.write_blob
        }
        self.extra_type_functions = dict()

    def register_type(self, the_type, write_func):
        self.extra_type_functions[the_type] = write_func

    def clear(self):
        self.datagram = PyDatagram()

    def get_datagram(self):
        return self.datagram

    def write(self, value):
        type_of_value = type(value)
        builtin_converter_func = self.builtin_type_functions.get(type_of_value)
        if builtin_converter_func is not None:
            builtin_converter_func(value)
        else:
            converter_func = self.extra_type_functions.get(type_of_value)
            if converter_func is not None:
                converter_func(self, value)
            else:
                raise Exception(f"Unsupported value type for DatagramWriter: {type(value).__name__}")

    def write_string(self, value):
        self.datagram.addString(value)

    def write_string32(self, value):
        self.datagram.addString32(value)

    def write_bool(self, value):
        self.datagram.addBool(value)

    def write_int8(self, value):
        self.datagram.addInt8(value)

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

    def write_vec2(self, value):
        self.write_float64(value[0])
        self.write_float64(value[1])

    def write_vec3(self, value):
        self.write_float64(value[0])
        self.write_float64(value[1])
        self.write_float64(value[2])

    def write_vec4(self, value):
        self.write_float64(value[0])
        self.write_float64(value[1])
        self.write_float64(value[2])
        self.write_float64(value[3])

    def write_tuple(self, value):
        for v in value:
            self.write(v)

    def write_list(self, value):
        self.write_int16(len(value))
        for v in value:
            self.write(v)


# Used internally by networking module.
class ExceedsListLimitException(Exception):
    pass


# -- Description --
# Main deserialization class used by the networking module.
class DatagramReader:
    def __init__(self):
        self.datagram = None
        self.iter = None
        self.builtin_read_functions = {
            bool: self.read_bool,
            int: self.read_int64,
            float: self.read_float64,
            str: self.read_string32,
            Vec2: self.read_vec2,
            Vec3: self.read_vec3,
            Vec4: self.read_vec4,
            bytes: self.read_blob

        }
        self.extra_read_functions = dict()

    def register_type(self, the_type, read_func):
        self.extra_read_functions[the_type] = read_func

    def set_datagram(self, datagram):
        self.datagram = datagram
        self.iter = PyDatagramIterator(self.datagram)

    def get_datagram(self):
        return self.datagram

    def set_datagram_from_blob(self, blob):
        self.set_datagram(p3d.Datagram(blob))

    def read(self, value_type, max_list_length=1000):
        builtin_converter_func = self.builtin_read_functions.get(value_type)
        if builtin_converter_func is not None:
            return builtin_converter_func()
        else:
            converter_func = self.extra_read_functions.get(value_type)
            if converter_func is not None:
                return converter_func(self)
            else:
                if type(value_type) is tuple:
                    origin_type = value_type[0]
                    if origin_type is tuple:
                        arg_types = value_type[1]
                        values = []
                        for arg_type in arg_types:
                            values.append(self.read(arg_type))
                        return tuple(values)
                    elif origin_type is list:
                        arg_type = value_type[1][0]
                        if arg_type is list:
                            raise Exception("DatagramReader does not support lists of lists.")
                        l = self.read_int16()
                        if l > max_list_length:
                            raise ExceedsListLimitException("Received list that exceeds the max list length allowed by the DatagramReader.")
                        values = []
                        for i in range(l):
                            values.append(self.read(arg_type))
                        return values
                    else:
                        raise Exception(f"Unsupported value type for DatagramReader: {value_type.__name__}")
                else:
                    raise Exception(f"Unsupported value type for DatagramReader: {value_type.__name__}")

    def read_string(self):
        return self.iter.getString()

    def read_string32(self):
        return self.iter.getString32()

    def read_bool(self):
        return self.iter.getBool()

    def read_int8(self):
        return self.iter.getInt8()

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

    def read_vec2(self):
        return Vec2(self.read_float64(), self.read_float64())

    def read_vec3(self):
        return Vec3(self.read_float64(), self.read_float64(), self.read_float64())

    def read_vec4(self):
        return Vec4(self.read_float64(), self.read_float64(), self.read_float64(), self.read_float64())


# Gives a 32 bit hash value (shifted one right (31 bit)) that is the same across runs and devices.
def procedure_hash(name):
    h = hashlib.sha1(name.encode("utf-8"), usedforsecurity=False).digest()
    return int.from_bytes(h[:4], byteorder="big") >> 1


# -- Description --
# Main remote procedure call class used by the networking module.
# This class is likely the one you are looking for.
# -- max list length --
# Lists are supported for remote procedure calls, but to prevent attacks involving giant lists,
# there is an upper limit on the length, this can be configured, the default is small on purpose.
# -- kwargs --
# The remaining keyword arguments are passed to Peer, see the Peer class for more information.
# -- Notes --
# The first two arguments passed to a remote procedure call are connection, and time_received.
# You can disable the printing of messages on connect and disconnect via the
# print_connect, and print_disconnect booleans.
# See the networking samples on how to use this class.
class RPCPeer:
    def __init__(self, max_list_length=16, **kwargs):
        self.peer = Peer(**kwargs)

        self.max_list_length = max_list_length

        self.print_connect = True
        self.print_disconnect = True

        def default_on_connect(connection, time_connected):
            connection.rpc_peer = self
            if self.print_connect:
                print("New connection:", connection.address)
            on_connects = self.procedures.get(procedure_hash("on_connect"))
            if on_connects is not None:
                for on_connect in reversed(on_connects):
                    host_only = on_connect[3]
                    client_only = on_connect[4]
                    if self.peer.is_hosting():
                        if not client_only:
                            on_connect[2](connection, time_connected)
                    else:
                        if not host_only:
                            on_connect[2](connection, time_connected)

        def default_on_disconnect(connection, time_disconnected):
            if self.print_disconnect:
                print("Disconnected:", connection.address)
            on_disconnects = self.procedures.get(procedure_hash("on_disconnect"))
            if on_disconnects is not None:
                for on_disconnect in reversed(on_disconnects):
                    host_only = on_disconnect[3]
                    client_only = on_disconnect[4]
                    if self.peer.is_hosting():
                        if not client_only:
                            on_disconnect[2](connection, time_disconnected)
                    else:
                        if not host_only:
                            on_disconnect[2](connection, time_disconnected)

        def on_data(connection, data, time_received):
            self.rpc_on_data(connection, data, time_received)

        if self.peer.on_connect is None:
            self.peer.on_connect = default_on_connect
        if self.peer.on_disconnect is None:
            self.peer.on_disconnect = default_on_disconnect
        self.peer.on_data = on_data

        self.procedures = dict()
        self.procedures[procedure_hash("on_connect")] = []
        self.procedures[procedure_hash("on_disconnect")] = []

        self.writer = DatagramWriter()
        self.reader = DatagramReader()

    def is_using_tls(self):
        return self.peer.is_using_tls()

    def start(self, host_name, port, is_host=False, backlog=100, tls_host_name=None, socket_address_family=None):
        return self.peer.start(host_name, port, is_host=is_host, backlog=backlog, tls_host_name=tls_host_name, socket_address_family=socket_address_family)

    def stop(self):
        self.peer.stop()

    def update(self, max_events=100):
        self.peer.update(max_events=max_events)

    def is_running(self):
        return self.peer.is_running()

    def is_hosting(self):
        return self.peer.is_hosting()

    def disconnect_all(self):
        self.peer.disconnect_all()

    def connection_count(self):
        return self.peer.connection_count()

    def get_connections(self):
        return self.peer.get_connections()

    def register_type(self, the_type, write_func, read_func):
        self.writer.register_type(the_type, write_func)
        self.reader.register_type(the_type, read_func)

    def register_procedure(self, proc, host_only=False, client_only=False, prefix=None):
        func_spec = inspect.getfullargspec(proc)
        if not len(func_spec.args) >= 2:
            raise Exception(f"{proc.__name__} must have at least two arguments, connection and time_received.")
        func_args = func_spec.args[2:]
        if func_spec.args[0] == "self":
            func_args = func_args[1:]
        arg_types = []
        for func_arg in func_args:
            func_arg_type = func_spec.annotations.get(func_arg)
            if not func_arg_type is not None:
                raise Exception(f"Failed to register the '{proc.__name__}' procedure, it's missing a type annotation for the '{func_arg}' argument.")
            if type(func_arg_type) is types.GenericAlias:
                arg_types.append((typing.get_origin(func_arg_type), typing.get_args(func_arg_type)))
            else:
                arg_types.append(func_arg_type)
        proc_name = proc.__name__
        if prefix is not None:
            proc_name = prefix + "_" + proc_name
        procedure_name_hash = procedure_hash(proc_name)
        if proc.__name__ in ("on_connect", "on_disconnect"):
            p = self.procedures.get(procedure_name_hash)
            p.append((proc_name, arg_types, proc, host_only, client_only))
        else:
            if not procedure_name_hash not in self.procedures:
                raise Exception(f"{proc_name} was already registered before.")
            self.procedures[procedure_name_hash] = (proc_name, arg_types, proc, host_only, client_only)

    def __getattr__(self, name):
        def remote_procedure(*args):
            if not len(args) >= 1:
                raise Exception(f"Remote procedure call '{name}' must have at least one argument, the connection.")
            if not isinstance(args[0], Connection):
                raise Exception(f"First argument to the RPC '{name}' must be a 'Connection' type.")
            procedure_name_hash = procedure_hash(name)
            self.writer.clear()
            self.writer.write_int32(procedure_name_hash)
            connection = args[0]
            for arg in args[1:]:
                self.writer.write(arg)
            connection.send(self.writer.get_datagram().getMessage())

        return remote_procedure

    def rpc_on_data(self, connection, data, time_received):
        self.reader.set_datagram(p3d.Datagram(data))

        proc_name = None
        proc_func = None
        proc_arg_values = None
        proc_arg_types = None
        host_only = False
        client_only = False

        try:
            procedure_name_hash = self.reader.read_int32()
            proc = self.procedures.get(procedure_name_hash)
            if proc is None:
                raise Exception("Remote attempted to call a RPC that does not exist (maybe a name typo in the source code?).")
            proc_name = proc[0]
            proc_arg_types = proc[1]
            proc_func = proc[2]
            host_only = proc[3]
            client_only = proc[4]
            proc_arg_values = []
            arg_type = None
            try:
                for t in proc_arg_types:
                    arg_type = t
                    v = self.reader.read(t, max_list_length=self.max_list_length)
                    proc_arg_values.append(v)
            except ExceedsListLimitException:
                raise Exception(f"Argument with type '{arg_type}' exceeds max list size limit for procedure '{proc_name}'.")
            except Exception as e:
                raise Exception(f"Received invalid or missing argument or list/tuple exceeding max length allowed for procedure '{proc_name}', expected a '{arg_type}'.\n    {str(e)}")
        except Exception as e:
            print("WARNING: Received invalid remote procedure call, disconnecting...")
            print(e)
            connection.disconnect()

        if proc_func is not None and proc_arg_types is not None and proc_arg_values is not None:
            if len(proc_arg_values) != len(proc_arg_types):
                print("WARNING: Received invalid remote procedure call, disconnecting...")
                print(f"Received an invalid number of arguments for procedure '{proc_name}'.")
                connection.disconnect()
            else:
                if self.peer.is_hosting():
                    if not client_only:
                        proc_func(connection, time_received, *proc_arg_values)
                else:
                    if not host_only:
                        proc_func(connection, time_received, *proc_arg_values)


# Convenience attribute applied to functions to register them as remote procedure calls.
#
# @rpc(my_rpc_peer_object)
# def foo(connection, time_received, x: int):
#     print(x)
def rpc(peer, host_only=False, client_only=False):
    def wrapper(f):
        peer.register_procedure(f, host_only=host_only, client_only=client_only)
    return wrapper


# Prevent error message spam from Panda3D network module.
p3d.loadPrcFileData("", "notify-level-net fatal")
