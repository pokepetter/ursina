from ursina.vec2 import Vec2
from ursina.vec3 import Vec3
from ursina.vec4 import Vec4

import panda3d.core as p3d

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from enum import Enum, auto

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

import threading
import asyncio

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

        self.async_task = None

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        return self.uid == other.uid

    def send(self, data):
        self.peer.send(self, data)

    def disconnect(self):
        self.peer.disconnect(self)

    def is_timed_out(self):
        return self.timed_out

    def is_connected(self):
        return self.connected


# Used internally by Peer.
class PeerEvent(Enum):
    ERROR = auto()
    CONNECT = auto()
    DISCONNECT = auto()
    DATA = auto()


# Used internally by Peer.
class PeerInput(Enum):
    ERROR = auto()
    SEND = auto()
    DISCONNECT = auto()
    DISCONNECT_ALL = auto()


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
        self.output_event_queue = deque()
        self.input_event_queue = deque()

        self.socket = None
        self.host_name = None
        self.tls_host_name = None
        self.port = None
        self.backlog = 100
        self.is_host = False

        self.running = False

        self.main_thread = None
        self.running_lock = threading.Lock()
        self.output_event_lock = threading.Lock()
        self.input_event_lock = threading.Lock()
        self.listen_task = None

        self.main_thread_sleep_time = 0.001
        self.ssl_handshake_sleep_time = 0.0001
        self.recv_ssl_sleep_time = 0.0001
        self.recv_unavailable_sleep_time = 0.0001

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

        self.output_event_queue.clear()
        self.input_event_queue.clear()

        self.main_thread = threading.Thread(target=self._start, daemon=True)
        self.main_thread.start()

    def stop(self):
        if not self.running:
            return

        with self.running_lock:
            self.running = False

        self.main_thread.join()

    def update(self, max_events=100):
        with self.output_event_lock:
            for i in range(max_events):
                if len(self.output_event_queue) == 0:
                    break
                next_event = self.output_event_queue.popleft()
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
        b = bytearray()
        b += struct.pack(">H", len(data))
        b += data

        with self.input_event_lock:
            self.input_event_queue.append((PeerInput.SEND, connection, b))

    def disconnect(self, connection):
        with self.input_event_lock:
            self.input_event_queue.append((PeerInput.DISCONNECT, connection, None))

    def disconnect_all(self):
        with self.input_event_lock:
            self.input_event_queue.append((PeerInput.DISCONNECT_ALL, None, None))

    def is_running(self):
        return self.running

    def is_hosting(self):
        return self.is_host

    def connection_count(self):
        return len(self.connections)

    def get_connections(self):
        return self.connections

    def _start(self):
        asyncio.run(self._run())

    def _add_connection(self, socket, address, async_loop):
        connection = Connection(self, socket, address, self.connection_timeout)
        connection_task = async_loop.create_task(self._receive(connection, async_loop))
        connection.async_task = connection_task
        self.connections.append(connection)
        with self.output_event_lock:
            self.output_event_queue.append((PeerEvent.CONNECT, connection, None, time.time()))

    async def _run(self):
        async_loop = asyncio.get_event_loop()

        if self.is_host:
            try:
                self.socket = socket.socket(self.socket_address_family, socket.SOCK_STREAM, 0)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind((self.host_name, self.port))
                self.socket.listen(self.backlog)
                self.socket.setblocking(False)
            except Exception as e:
                print(e)
                self.running = False
                raise

            self.listen_task = asyncio.create_task(self._listen(async_loop))
        else:
            client_socket = None
            if self.use_tls:
                try:
                    self.socket = socket.socket(self.socket_address_family, socket.SOCK_STREAM, 0)
                    client_socket = self.ssl_context.wrap_socket(self.socket, server_hostname=self.tls_host_name)
                    client_socket.connect((self.host_name, self.port))
                except Exception as e:
                    print(e)
                    self.running = False
                    return
            else:
                try:
                    client_socket = socket.create_connection((self.host_name, self.port))
                except Exception as e:
                    print(e)
                    self.running = False
                    return
            try:
                client_socket.setblocking(False)
                client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self._add_connection(client_socket, (self.host_name, self.port), async_loop)
            except Exception as e:
                print(e)
                self.running = False
                return

        with self.running_lock:
            self.running = True

        while self.running:
            to_be_removed = []
            with self.input_event_lock:
                while len(self.input_event_queue) > 0:
                    next_event = self.input_event_queue.popleft()
                    event = next_event[0]
                    connection = next_event[1]
                    data = next_event[2]
                    if event == PeerInput.SEND:
                        try:
                            connection.socket.sendall(data)
                        except:
                            to_be_removed.append(connection)
                    elif event == PeerInput.DISCONNECT:
                        to_be_removed.append(connection)
                    elif event == PeerInput.DISCONNECT_ALL:
                        for connection in self.connections:
                            to_be_removed.append(connection)
            for connection in to_be_removed:
                connection.async_task.cancel()
                try:
                    await connection.async_task
                except:
                    pass
            await asyncio.sleep(self.main_thread_sleep_time)

        for connection in self.connections:
            connection.async_task.cancel()
            try:
                await connection.async_task
            except:
                pass

        if self.is_host:
            self.listen_task.cancel()
            try:
                await self.listen_task
            except:
                pass

    async def _listen(self, async_loop):
        try:
            while True:
                client_socket, client_address = await async_loop.sock_accept(self.socket)
                if self.use_tls:
                    socket_wrap_failed = True
                    try:
                        client_socket = self.ssl_context.wrap_socket(client_socket, server_side=True, do_handshake_on_connect=False)
                        socket_wrap_failed = False
                    except Exception as e:
                        pass
                    if socket_wrap_failed:
                        try:
                            client_socket.close()
                        except:
                            pass
                        continue
                    handshake_failed = True
                    while True:
                        try:
                            client_socket.do_handshake()
                            handshake_failed = False
                            break
                        except ssl.SSLWantReadError as e:
                            await asyncio.sleep(self.ssl_handshake_sleep_time)
                        except ssl.SSLWantWriteError as e:
                            await asyncio.sleep(self.ssl_handshake_sleep_time)
                        except Exception as e:
                            break
                    if handshake_failed:
                        try:
                            client_socket.close()
                        except:
                            pass
                        continue
                client_socket.setblocking(False)
                client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self._add_connection(client_socket, client_address, async_loop)
        except asyncio.CancelledError:
            pass
        finally:
            try:
                self.socket.close()
            except:
                pass

    async def _recv(self, connection, async_loop):
        data = None
        while True:
            try:
                data = connection.socket.recv(connection.expected_byte_count)
                break
            except ssl.SSLWantReadError:
                await asyncio.sleep(self.recv_ssl_sleep_time)
            except ssl.SSLWantWriteError:
                await asyncio.sleep(self.recv_ssl_sleep_time)
            except BlockingIOError:
                await asyncio.sleep(self.recv_unavailable_sleep_time)
            except Exception as e:
                raise
        return data

    async def _receive(self, connection, async_loop):
        try:
            while True:
                data = None
                try:
                    if connection.connection_timeout is None:
                        data = await self._recv(connection, async_loop)
                    else:
                        data = await asyncio.wait_for(self._recv(connection, async_loop), timeout=connection.connection_timeout)
                except asyncio.exceptions.TimeoutError:
                    connection.timed_out = True
                    raise
                except Exception as e:
                    print(e)
                    raise
                if data is None:
                    break
                if len(data) == 0:
                    break
                connection.bytes_received += data
                connection.expected_byte_count -= len(data)

                if connection.expected_byte_count == 0:
                    if connection.state == "l":
                        l = struct.unpack(">H", connection.bytes_received)[0]
                        connection.state = "c"
                        connection.expected_byte_count = l
                        connection.bytes_received.clear()
                    elif connection.state == "c":
                        d = bytes(connection.bytes_received.copy())
                        with self.output_event_lock:
                            self.output_event_queue.append((PeerEvent.DATA, connection, d, time.time()))
                        connection.state = "l"
                        connection.expected_byte_count = connection.length_byte_count
                        connection.bytes_received.clear()
        except asyncio.CancelledError:
            pass
        except:
            pass
        finally:
            try:
                connection.socket.close()
            except:
                pass
            connection.state = "l"
            connection.bytes_received.clear()
            connection.expected_byte_count = connection.length_byte_count
            connection.connected = False
            self.connections.remove(connection)
            with self.output_event_lock:
                self.output_event_queue.append((PeerEvent.DISCONNECT, connection, None, None))
            if not self.is_host:
                self.running = False


# -- Description --
# Main serialization class used by the networking module.
class DatagramWriter:
    def __init__(self):
        self.datagram = PyDatagram()
        self.type_functions = dict()

    def register_type(self, the_type, write_func):
        self.type_functions[the_type] = write_func

    def clear(self):
        self.datagram = PyDatagram()

    def get_datagram(self):
        return self.datagram

    def write(self, value):
        converter_func = self.type_functions.get(type(value))
        if converter_func is not None:
            converter_func(self, value)
        else:
            if isinstance(value, bool):
                self.write_bool(value)
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
                self.write_int16(len(value))
                for v in value:
                    self.write(v)
            elif isinstance(value, bytes):
                self.write_blob(value)
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


# Used internally by networking module.
class ExceedsListLimitException(Exception):
    pass


# -- Description --
# Main deserialization class used by the networking module.
class DatagramReader:
    def __init__(self):
        self.datagram = None
        self.iter = None
        self.read_functions = dict()

    def register_type(self, the_type, read_func):
        self.read_functions[the_type] = read_func

    def set_datagram(self, datagram):
        self.datagram = datagram
        self.iter = PyDatagramIterator(self.datagram)

    def get_datagram(self):
        return self.datagram

    def set_datagram_from_blob(self, blob):
        self.set_datagram(p3d.Datagram(blob))

    def read(self, value_type, max_list_length=1000):
        converter_func = self.read_functions.get(value_type)
        if converter_func is not None:
            return converter_func(self)
        else:
            if value_type is bool:
                return self.read_bool()
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
            elif type(value_type) is tuple:
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
            elif value_type is bytes:
                return self.read_blob()
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
                print("Received an invalid number of arguments for procedure '{proc_name}'.")
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
