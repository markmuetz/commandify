'''Decorators/functions for turning functions into command line arguments'''
from collections import OrderedDict
from argparse import ArgumentParser
from functools import wraps


_commands = OrderedDict()
_main_commands = OrderedDict()


def main_command(*dec_args, **dec_kwargs):
    '''Decorator for adding to main function (entry point)

    Should only be applied to one function'''
    return _store_command(dec_args, dec_kwargs, _main_commands)


def command(*dec_args, **dec_kwargs):
    '''Decorator for adding to sub commands'''
    return _store_command(dec_args, dec_kwargs, _commands)


def _store_command(dec_args, dec_kwargs, command_container):
    if len(dec_args) == 1 and callable(dec_args[0]):
        func = dec_args[0]
        command_container[func.__name__] = (func, [], {})

        # Preserve e.g. docstring.
        @wraps(func)
        def decorator_wrapper(*func_args, **func_kwargs):
            return func(*func_args, **func_kwargs)
        return decorator_wrapper
    else:

        def decorator(func):
            command_container[func.__name__] = (func, dec_args, dec_kwargs)

            # Preserve e.g. docstring.
            @wraps(func)
            def decorator_wrapper(*func_args, **func_kwargs):
                return func(*func_args, **func_kwargs)
        return decorator


class _NoDefaultClass(object):
    '''private class used to indicate that there is no default

    Better than using None'''
    pass


class CommandifyError(Exception):
    '''Exceptions thrown by commandify'''
    def __init__(self, message, error_type='code'):
        super(CommandifyError, self).__init__(message)
        if error_type not in ['code', 'user']:
            raise Exception('Error type {0} not understood'.format(error_type))
        self.error_type = error_type


def _add_commands_to_parser(command, parser, dec_args, dec_kwargs,
                            provide_args=[]):
    # Work out defaults for each command, set all defaults to _NoDefaultClass
    # then loop over default args (as defined in function signature) settings
    # them as necessary.
    defaults = [_NoDefaultClass] * command.__code__.co_argcount
    if command.__defaults__:
        for i in range(1, len(command.__defaults__) + 1):
            defaults[-i] = command.__defaults__[-i]

    # Loop over varnames (function argument names) and defaults, adding an
    # argparse argument.
    for varname, default in zip(command.__code__.co_varnames, defaults):
        if varname == 'args' or varname in provide_args:
            # args is ignored so its default should not be set.
            if default != _NoDefaultClass:
                raise CommandifyError(
                    'Should not set a default value for args keyword')
            else:
                continue
        # Get the decorator arguments which will be used in
        # parser.add_argument(...).
        if varname in dec_kwargs:
            arg_kwargs = dec_kwargs.pop(varname)
        else:
            arg_kwargs = {}

        argname = varname.replace('_', '-')
        arg_args = ['--{0}'.format(argname)]
        # 'flag' is a special arg. keyword, it (e.g. 'flag': '-a')
        if 'flag' in arg_kwargs:
            flag = arg_kwargs.pop('flag')
            arg_args.append(flag)

        # Default can either be set in the function arguments or as a an option
        # to the command(...) decorator.
        if 'default' in arg_kwargs and default != _NoDefaultClass:
            raise CommandifyError('default set twice for function/method {0}'
                                  .format(command.__name__))
        if 'default' in arg_kwargs:
            default = arg_kwargs.pop('default')

        # Add the command line argument.
        if default != _NoDefaultClass:
            parser.add_argument(*arg_args, default=default, **arg_kwargs)
        else:
            # Any arguments without a default are required.
            parser.add_argument(*arg_args, required=True, **arg_kwargs)
    # Check all decorator args have been accounted for.
    if dec_kwargs:
        raise CommandifyError('Unexpected command options: {0}'
                              .format(', '.join(dec_kwargs.keys())))


def _get_command_args(command, args, provide_args):
    '''Work out the command arguments for a given command'''
    command_args = {}

    for varname in command.__code__.co_varnames:
        if varname == 'args':
            command_args['args'] = args
        elif varname in provide_args:
            command_args[varname] = provide_args[varname]
        else:
            command_args[varname] = getattr(args, varname)
    return command_args


class CommandifyArgumentParser(ArgumentParser):
    def __init__(self, provide_args={}, debug=False, *args, **kwargs):
        super(CommandifyArgumentParser, self).__init__(*args, **kwargs)
        self.provide_args = provide_args
        self.debug = debug

    def setup_arguments(self):
        try:
            if len(_main_commands) == 0:
                raise CommandifyError('No main_command defined\n'
                                      'Please add the @main_command decorator '
                                      'to one function')
            elif len(_main_commands) > 1:
                raise CommandifyError('More than one main_command defined\n'
                                      'Please add the @main_command decorator '
                                      'to only one function')

            # Setup main command.
            main_command, main_args, main_kwargs =\
                list(_main_commands.values())[0]
            main_doc = main_command.__doc__
            description = main_doc.split('\n')[0] if main_doc else None
            _add_commands_to_parser(main_command, self,
                                    main_args, main_kwargs, self.provide_args)

            # Setup subcommands.
            subparsers = self.add_subparsers(dest='command')
            for name, (command, dec_args, dec_kwargs) in _commands.items():
                if command.__doc__:
                    help = command.__doc__.split('\n')[0]
                else:
                    help = None
                subparser = subparsers.add_parser(name, help=help)
                _add_commands_to_parser(command, subparser,
                                        dec_args, dec_kwargs,
                                        self.provide_args)

        except CommandifyError as e:
            if e.error_type == 'user':
                self.print_help()
            self.exit(status=1,
                      message='{0}: error: {1}\n'.format(self.prog, e))

    def parse_args(self, *args, **kwargs):
        self.args = super(CommandifyArgumentParser, self).parse_args(*args,
                                                                     **kwargs)
        return self.args

    def dispatch_commands(self):
        try:
            if self.args.command is None:
                raise CommandifyError('too few arguments', 'user')

            command, _, _ = _commands[self.args.command]

            # Get arguments for both commands.
            # Bad choice of name: main_command, clashes with function.
            main_command, main_args, main_kwargs =\
                list(_main_commands.values())[0]
            main_command_args = _get_command_args(main_command, self.args,
                                                  self.provide_args)
            command_args = _get_command_args(command, self.args,
                                             self.provide_args)

            # Run commands.
            main_command(**main_command_args)
            command(**command_args)
        except CommandifyError as e:
            if e.error_type == 'user':
                parser.print_help()
            parser.exit(status=1,
                        message='{0}: error: {1}\n'.format(parser.prog, e))


def commandify():
    '''Turns decorated functions into command line args

    Finds the main_command and all commands and generates command line args
    from these.'''
    parser = CommandifyArgumentParser()
    parser.setup_arguments()
    args = parser.parse_args()
    parser.dispatch_commands()
    parser.exit(status=0)


def _commandify_old():
    print('Warning, deprecated, please use commandify instead')
    parser = ArgumentParser(add_help=False)
    try:
        if len(_main_commands) == 0:
            raise CommandifyError('No main_command defined\n'
                                  'Please add the @main_command decorator to '
                                  'one function')
        elif len(_main_commands) > 1:
            raise CommandifyError('More than one main_command defined\n'
                                  'Please add the @main_command decorator to '
                                  'only one function')

        # Setup main command.
        main_command, main_args, main_kwargs = list(_main_commands.values())[0]
        main_doc = main_command.__doc__
        description = main_doc.split('\n')[0] if main_doc else None
        parser = ArgumentParser(description=description)
        _add_commands_to_parser(main_command, parser, main_args, main_kwargs)

        # Setup subcommands.
        subparsers = parser.add_subparsers(dest='command')
        for name, (command, dec_args, dec_kwargs) in _commands.items():
            if command.__doc__:
                help = command.__doc__.split('\n')[0]
            else:
                help = None
            subparser = subparsers.add_parser(name, help=help)
            _add_commands_to_parser(command, subparser, dec_args, dec_kwargs)

        # Parse commands and work out which one user has chosen.
        args = parser.parse_args()
        if args.command is None:
            raise CommandifyError('too few arguments', 'user')

        command, _, _ = _commands[args.command]

        # Get arguments for both commands.
        main_command_args = _get_command_args(main_command, args)
        command_args = _get_command_args(command, args)

        # Run commands.
        main_command(**main_command_args)
        command(**command_args)
    except CommandifyError as e:
        if e.error_type == 'user':
            parser.print_help()
        parser.exit(status=1,
                    message='{0}: error: {1}\n'.format(parser.prog, e))

    parser.exit(status=0)
