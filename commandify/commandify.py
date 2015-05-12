'''Decorators/functions for turning functions into command line arguments'''
from collections import OrderedDict
from argparse import ArgumentParser


_commands = OrderedDict()
_main_command = OrderedDict()


def main_command(*dec_args, **dec_kwargs):
    '''Decorator for adding to main function (entry point)

    Should only be applied to one function'''
    return _store_command(dec_args, dec_kwargs, _main_command)


def command(*dec_args, **dec_kwargs):
    '''Decorator for adding to sub commands'''
    return _store_command(dec_args, dec_kwargs, _commands)


def _store_command(dec_args, dec_kwargs, command_container):
    if len(dec_args) == 1 and callable(dec_args[0]):
        command_container[dec_args[0].func_name] = (dec_args[0], [], {})

        def decorator_wrapper(*func_args, **func_kwargs):
            return func(*func_args, **func_kwargs)
        return decorator_wrapper
    else:

        def decorator(func):
            command_container[func.func_name] = (func, dec_args, dec_kwargs)

            def decorator_wrapper(*func_args, **func_kwargs):
                return func(*func_args, **func_kwargs)
        return decorator


class _NoDefaultClass(object):
    '''private class used to indicate that there is no default

    Better than using None'''
    pass


def _add_commands_to_parser(command, parser, dec_args, dec_kwargs):
    # Work out defaults for each command, set all defaults to _NoDefaultClass
    # then loop over default args (as defined in function signature) settings
    # them as necessary.
    defaults = [_NoDefaultClass] * command.func_code.co_argcount
    if command.func_defaults:
        for i in range(1, len(command.func_defaults) + 1):
            defaults[-i] = command.func_defaults[-i]

    # Loop over varnames (function argument names) and defaults, adding an
    # argparse argument.
    for varname, default in zip(command.func_code.co_varnames, defaults):
        if varname == 'args':
            # args is ignored so its default should not be set.
            if default != _NoDefaultClass:
                raise Exception(
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
            raise Exception('default set twice for function/method {0}'
                            .format(command.func_name))
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
        raise Exception('Unexpected command options: {0}'
                        .format(', '.join(dec_kwargs.keys())))


def _get_command_args(command, args):
    '''Work out the command arguments for a given command'''
    command_args = {}

    for varname in command.func_code.co_varnames:
        if varname == 'args':
            command_args['args'] = args
        else:
            command_args[varname] = getattr(args, varname)
    return command_args


def commandify():
    '''Turns decorated functions into command line args

    Finds the main_command and all commands and generates command line args
    from these.'''
    parser = ArgumentParser()
    try:
        if len(_main_command) == 0:
            raise Exception('No main_command defined\n'
                            'Please add the @main_command decorator to one'
                            'function')
        elif len(_main_command) > 1:
            raise Exception('More than one main_command defined\n'
                            'Please add the @main_command decorator to only'
                            'one function')

        # Setup main command.
        main_command, main_args, main_kwargs = _main_command.values()[0]
        parser = ArgumentParser(usage=main_command.__doc__)
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
        command, _, _ = _commands[args.command]

        # Get arguments for both commands.
        main_command_args = _get_command_args(main_command, args)
        command_args = _get_command_args(command, args)

        # Run commands.
        main_command(**main_command_args)
        command(**command_args)
    except Exception, e:
        parser.exit(status=1, message='Error: {0}\n'.format(e.message))

    parser.exit(status=0)
