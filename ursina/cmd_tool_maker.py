import inspect
import functools
import sys


def auto_validate_input(cls):
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith('_'):
            original_method = attr_value
            sig = inspect.signature(original_method)
            @functools.wraps(original_method)
            def wrapper(self, *args, __method=original_method, __sig=sig, **kwargs):
                bound = __sig.bind(self, *args, **kwargs)
                bound.apply_defaults()
                # Validate and convert types
                for name, value in bound.arguments.items():
                    if name == 'self':
                        continue
                    param = __sig.parameters[name]
                    expected_type = param.annotation
                    if expected_type == inspect._empty:
                        # fallback: try type of default
                        default_val = param.default
                        if default_val != inspect.Parameter.empty:
                            expected_type = type(default_val)
                        else:
                            continue
                    # Skip None (could allow optional)
                    if value is None:
                        continue
                    try:
                        # Simple conversion, skip if already correct type
                        if not isinstance(value, expected_type):
                            # Special bool handling
                            if expected_type is bool and isinstance(value, str):
                                val_lower = value.lower()
                                if val_lower in ('true','1','yes'):
                                    bound.arguments[name] = True
                                elif val_lower in ('false','0','no'):
                                    bound.arguments[name] = False
                                else:
                                    raise ValueError(f'Invalid bool string for {name}')
                            else:
                                bound.arguments[name] = expected_type(value)
                    except Exception as e:\
                        raise ValueError(f'Argument \'{name}\' must be of type {expected_type.__name__}. Got value \'{value}\'. Error: {e}')
                return __method(*bound.args, **bound.kwargs)
            setattr(cls, attr_name, wrapper)
    return cls


def auto_log_function(function):
    '''Decorator to log function calls and their arguments.'''
    sig = inspect.signature(function)

    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):
        bound = sig.bind(self, *args, **kwargs)
        bound.apply_defaults()

        args_str = ', '.join(
            f'{k}={v!r}' for k, v in list(bound.arguments.items())[1:]  # skip self
        )
        print('\n  ' + ('-'*24))
        print(f'  calling {function.__name__}({args_str})')

        return function(*bound.args, **bound.kwargs)
    return wrapper

def auto_log_method_calls(cls):
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith('_'):
            setattr(cls, attr_name, auto_log_function(attr_value))
    return cls


def make_command_line_app(cls):
    args = sys.argv[1:]
    if not args or '--help' in args or '-h' in args:
        print_app_help(cls)
        sys.exit(0)

    # Parse __init__ parameters
    init_sig = inspect.signature(cls.__init__)
    init_params = list(init_sig.parameters.items())[1:]  # skip self

    init_kwargs = {}
    remaining_args = args[:]
    for name, param in init_params:
        if remaining_args:
            raw_value = remaining_args.pop(0)
            expected_type = param.annotation if param.annotation != inspect._empty else str
            init_kwargs[name] = parse_value(raw_value, expected_type)
        elif param.default == inspect.Parameter.empty:
            print(f'Missing required argument: {name}')
            print_app_help(cls)
            sys.exit(1)

    instance = cls(**init_kwargs)

    # Remaining arguments are method calls + their kwargs
    last_method_name = None  # track last method called

    i = 0
    while i < len(remaining_args):
        cmd = remaining_args[i]
        i += 1

        if not hasattr(instance, cmd):
            print(f'Unknown command: {cmd}')
            print_app_help(cls)
            sys.exit(1)

        last_method_name = cmd
        method = getattr(instance, cmd)
        method_sig = inspect.signature(method)
        args = []
        kwargs = {}

        while i < len(remaining_args):
            token = remaining_args[i]

            if token == '--':
                # User typed '--' alone — invalid here
                print(f"Unexpected '--' found while parsing arguments for '{last_method_name}'.")
                print_valid_method_args(cls, last_method_name)
                sys.exit(1)

            if token.startswith('--'):
                if '=' not in token:
                    print(f"Missing value for argument '{token}'. Use --{token[2:]}=value format.")
                    print_valid_method_args(cls, last_method_name)
                    sys.exit(1)

                k, v = token[2:].split('=', 1)
                if v == '':
                    print(f"Empty value provided for argument '{k}'.")
                    print_valid_method_args(cls, last_method_name)
                    sys.exit(1)

                if k not in method_sig.parameters:
                    print(f"Unknown argument '{k}' for method '{last_method_name}'.")
                    print_valid_method_args(cls, last_method_name)
                    sys.exit(1)

                param = method_sig.parameters.get(k)
                expected_type = param.annotation if param and param.annotation != inspect._empty else str
                kwargs[k] = parse_value(v, expected_type)
                i += 1
            else:
                # Next token is either another command or invalid
                break

        method(*args, **kwargs)


def print_valid_method_args(obj, method_name):
    def get_original_method_sig(obj, method_name):
        method = getattr(obj, method_name)
        # Unwrap decorators if possible
        while hasattr(method, "__wrapped__"):
            method = method.__wrapped__
        return inspect.signature(method)

    sig = get_original_method_sig(obj, method_name)
    print(f"\nValid arguments for method '{method_name}':")
    params = list(sig.parameters.items())[1:]  # skip self
    if not params:
        print("  (no arguments)")
        return
    for param_name, param in params:
        if param.default != inspect.Parameter.empty:
            default_val = param.default
            if isinstance(default_val, str):
                print(f"  --{param_name}='{default_val}'")
            else:
                print(f"  --{param_name}={default_val}")
        else:
            print(f"  --{param_name}=<required>")


def parse_value(value, expected_type):
    try:
        if expected_type == bool:
            return value.lower() in ('true', '1', 'yes')
        return expected_type(value)
    except Exception:
        raise ValueError(f'Expected type {expected_type} but got \'{value}\'')

def print_app_help(cls):
    init_sig = inspect.signature(cls.__init__)
    print(f'\nUsage:\n  {sys.argv[0]} <constructor args> <method> [--arg=value] ...\n')

    print('Constructor arguments:')
    for name, param in list(init_sig.parameters.items())[1:]:  # skip self
        param_type = param.annotation.__name__ if param.annotation != inspect._empty else 'str'
        required = param.default == inspect.Parameter.empty
        default = f'(default={param.default})' if not required else ''
        print(f'  {name} : {param_type} {'[required]' if required else '[optional]'} {default}')

    print('\nAvailable methods:')
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith('_'):
            continue
        sig = inspect.signature(method)
        doc = inspect.getdoc(method) or ''

        cli_args = []
        for param_name, param in list(sig.parameters.items())[1:]:  # skip self
            default = (
                f'={param.default!r}'
                if param.default != inspect.Parameter.empty else ''
            )
            cli_args.append(f'--{param_name}{default}')
        arg_str = ' '.join(cli_args)

        # Extract one-line summary from docstring or inline comment
        inline_description = '# '+doc.splitlines()[0] if doc else ''
        print(f'  {name} {arg_str}  {inline_description}')