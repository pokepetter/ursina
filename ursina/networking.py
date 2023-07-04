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

class Connection:
    def __init__(self, peer, socket, address):
        self.peer = peer
        self.socket = socket
        self.address = address

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


class PeerEvent(Enum):
    ERROR = auto()
    CONNECT = auto()
    DISCONNECT = auto()
    DATA = auto()


class PeerInput(Enum):
    ERROR = auto()
    SEND = auto()
    DISCONNECT = auto()
    DISCONNECT_ALL = auto()


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
            raise Exception("Invalid/unsupported socket address family '{}'.".format(socket_address_family))

        self.ssl_context = None

        self.connections = []
        self.output_event_queue = deque()
        self.input_event_queue = deque()

        self.socket = None
        self.secure_socket = None
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

    def start(self, host_name, port, is_host=False, backlog=100, tls_host_name=None, socket_address_family=None):
        if self.running:
            self.stop()

        if socket_address_family is not None:
            if socket_address_family == "INET":
                self.socket_address_family = socket.AF_INET
            elif socket_address_family == "INET6":
                self.socket_address_family = socket.AF_INET6
            else:
                raise Exception("Invalid/unsupported socket address family '{}'.".format(socket_address_family))

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
                d = next_event[2]
                t = next_event[3]
                if next_event[0] == PeerEvent.CONNECT:
                    if self.on_connect is not None:
                        self.on_connect(next_event[1], t)
                elif next_event[0] == PeerEvent.DISCONNECT:
                    if self.on_disconnect is not None:
                        self.on_disconnect(next_event[1], t)
                elif next_event[0] == PeerEvent.DATA:
                    if self.on_raw_data is not None:
                        d = self.on_raw_data(next_event[1], d, t)
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
        connection = Connection(self, socket, address)
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
                self.running = False
                raise
            
            if self.use_tls:
                try:
                    self.secure_socket = self.ssl_context.wrap_socket(self.socket, server_side=True)
                except Exception as e:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.running = False
                    raise

            self.listen_task = asyncio.create_task(self._listen(async_loop))
        else:
            client_socket = None
            try:
                client_socket = socket.create_connection((self.host_name, self.port))
            except Exception as e:
                self.running = False
                return
            try:
                if self.use_tls:
                    try:
                        secure_socket = self.ssl_context.wrap_socket(client_socket, server_hostname=self.tls_host_name)
                        client_socket = secure_socket
                    except Exception as e:
                        print(e)
                        raise e
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
            server_socket = self.socket
            if self.use_tls:
                server_socket = self.secure_socket

            while True:
                client_socket, client_address = await async_loop.sock_accept(server_socket)
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                if self.connection_timeout is not None:
                    client_socket.settimeout(self.connection_timeout)
                self._add_connection(client_socket, client_address, async_loop)
        except asyncio.CancelledError:
            pass
        finally:
            try:
                if self.use_tls:
                    self.secure_socket.close()
            except:
                pass
            try:
                self.socket.close()
            except:
                pass

    async def _receive(self, connection, async_loop):
        try:
            while True:
                try:
                    data = await async_loop.sock_recv(connection.socket, connection.expected_byte_count)
                except socket.timeout:
                    connection.timed_out = True
                    raise
                except:
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
            else:
                raise Exception("Unspported value type for DatagramWriter: {0}".format(type(value).__name__))

    def write_string(self, value):
        self.datagram.addString(value)

    def write_string32(self, value):
        self.datagram.addString32(value)

    def write_bool(self, value):
        self.datagram.addBool(value)

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


class ExceedsListLimitException(Exception):
    pass


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
                    raise Exception("Unspported value type for DatagramReader: {0}".format(value_type.__name__))
            else:
                raise Exception("Unspported value type for DatagramReader: {0}".format(value_type.__name__))

    def read_string(self):
        return self.iter.getString()

    def read_string32(self):
        return self.iter.getString32()

    def read_bool(self):
        return self.iter.getBool()

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
            on_connect = self.procedures.get(procedure_hash("on_connect"))
            if on_connect is not None:
                on_connect[2](connection, time_connected)

        def default_on_disconnect(connection, time_disconnected):
            if self.print_disconnect:
                print("Disconnected:", connection.address)
            on_disconnect = self.procedures.get(procedure_hash("on_disconnect"))
            if on_disconnect is not None:
                on_disconnect[2](connection, time_disconnected)

        def on_data(connection, data, time_received):
            self.rpc_on_data(connection, data, time_received)

        if self.peer.on_connect is None:
            self.peer.on_connect = default_on_connect
        if self.peer.on_disconnect is None:
            self.peer.on_disconnect = default_on_disconnect
        self.peer.on_data = on_data

        self.procedures = dict()

        self.writer = DatagramWriter()
        self.reader = DatagramReader()

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

    def register_procedure(self, proc, host_only=False, client_only=False):
        func_spec = inspect.getfullargspec(proc)
        arg_types = []
        assert len(func_spec.args) >= 2, "{} must have at least two arguments, connection and time_received.".format(proc.__name__)
        for func_arg in func_spec.args[2:]:
            func_arg_type = func_spec.annotations.get(func_arg)
            assert func_arg_type is not None, "Failed to register the '{}' procedure, it's missing a type annotation for the '{}' argument.".format(proc.__name__, func_arg)
            if type(func_arg_type) is types.GenericAlias:
                arg_types.append((typing.get_origin(func_arg_type), typing.get_args(func_arg_type)))
            else:
                arg_types.append(func_arg_type)
        procedure_name_hash = procedure_hash(proc.__name__)
        assert procedure_name_hash not in self.procedures, "{} was already registered before.".format(proc.__name__)
        self.procedures[procedure_name_hash] = (proc.__name__, arg_types, proc, host_only, client_only)

    def __getattr__(self, name):
        def remote_procedure(*args):
            assert len(args) >= 1, "Remote prcoedure call '{}' must have at least one argument, the connection.".format(name)
            assert isinstance(args[0], Connection), "First argument to the RPC '{}' must be a 'Connection' type.".format(name)
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
            if (host_only and not self.peer.is_hosting()) or (client_only and self.peer.is_hosting()):
                raise Exception("Remote attempted to call '{}' that is restricted to host only or client only.".format(proc_name))
            proc_arg_values = []
            arg_type = None
            try:
                for t in proc_arg_types:
                    arg_type = t
                    v = self.reader.read(t, max_list_length=self.max_list_length)
                    proc_arg_values.append(v)
            except ExceedsListLimitException:
                raise Exception("Argument with type '{}' exceeds max list size limit for procedure '{}'.".format(arg_type, proc_name))
            except:
                raise Exception("Received invalid or missing argument or list/tuple exceeding max length allowed for procedure '{}', expected a '{}'.".format(proc_name, arg_type))
        except Exception as e:
            print("WARNING: Received invalid remote procedure call, disconnecting...")
            print(e)
            connection.disconnect()

        if proc_func is not None and proc_arg_types is not None and proc_arg_values is not None:
            if len(proc_arg_values) != len(proc_arg_types):
                print("WARNING: Received invalid remote procedure call, disconnecting...")
                print("Received an invalid number of arguments for procedure '{}'.".format(proc_name))
                connection.disconnect()
            else:
                proc_func(connection, time_received, *proc_arg_values)


# Convenience attribute applied to functions to register them as remote procedure calls.
#
# @rpc(my_rpc_peer_object)
# def foo(x: int):
#     print(x)
def rpc(peer, host_only=False, client_only=False):
    def wrapper(f):
        peer.register_procedure(f, host_only=host_only, client_only=client_only)
    return wrapper


# Prevent error message spam from Panda3D network module.
p3d.loadPrcFileData("", "notify-level-net fatal")
