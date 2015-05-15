# Borrows heavily from argparse tests.
# Doesn't use meta class to setup tests.
import sys
import unittest
from collections import OrderedDict

import commandify as cmdify
print(cmdify._main_commands)

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class StdIOBuffer(StringIO):
    pass


class NS(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        sorted_items = sorted(self.__dict__.items())
        kwarg_str = ', '.join(['%s=%r' % tup for tup in sorted_items])
        return '%s(%s)' % (type(self).__name__, kwarg_str)

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __ne__(self, other):
        return not (self == other)


class ArgumentParserError(Exception):
    def __init__(self, message, stdout=None, stderr=None, error_code=None):
        Exception.__init__(self, message, stdout, stderr)
        self.message = message
        self.stdout = stdout
        self.stderr = stderr
        self.error_code = error_code


def turn_system_exit_into_error(func, *args, **kwargs):
    ### TAKEN FROM argparse ###
    # if called recursively just calls func
    # else redirects stdout, stderr and calls func, catching
    # and SystemExit exceptions. Always reconnects stdout/stderr
    # Don't fully understand - particularly commanted out part.

    # if this is being called recursively and stderr or stdout is already being
    # redirected, simply call the function and let the enclosing function
    # catch the exception
    if isinstance(sys.stderr, StdIOBuffer) or isinstance(sys.stdout, StdIOBuffer):
        return func(*args, **kwargs)

    # if this is not being called recursively, redirect stderr and
    # use it as the ArgumentParserError message
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StdIOBuffer()
    sys.stderr = StdIOBuffer()

    try:
        try:
            result = func(*args, **kwargs)
            # Not sure what this does?
            # for key in list(vars(result)):
            #     if getattr(result, key) is sys.stdout:
            #         setattr(result, key, old_stdout)
            #     if getattr(result, key) is sys.stderr:
            #         setattr(result, key, old_stderr)
            return result
        except SystemExit:
            code = sys.exc_info()[1].code
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
            raise ArgumentParserError("SystemExit", stdout, stderr, code)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


class ErrorRaisingArgumentParser(cmdify.CommandifyArgumentParser):
    '''Allows testing of argument parser errors.
    
    Instead of raising SystemExit will raise ArgumentParserError.
    Performs some tricks to redirect stdout/stderr too.'''
    def parse_args(self, *args, **kwargs):
        parse_args = super(ErrorRaisingArgumentParser, self).parse_args
        return turn_system_exit_into_error(parse_args, *args, **kwargs)

    def exit(self, *args, **kwargs):
        exit = super(ErrorRaisingArgumentParser, self).exit
        return turn_system_exit_into_error(exit, *args, **kwargs)

    def error(self, *args, **kwargs):
        error = super(ErrorRaisingArgumentParser, self).error
        return turn_system_exit_into_error(error, *args, **kwargs)


class BaseUnitTest(unittest.TestCase):
    def setUp(self):
        self.parser = ErrorRaisingArgumentParser()
        cmdify._commands = OrderedDict()
        cmdify._main_commands = OrderedDict()

    def _run_dispatch_tests(self, failures, successes):
        self.parser.setup_arguments()
        self._test_failures(failures)
        self._test_dispatch_successes(successes)

    def _test_failures(self, failures):
        for args in failures:
            print(args)
            if isinstance(args, tuple):
                test_ns = True
                args, expected_ns = args[0], args[1]
            else:
                test_ns = False

            if isinstance(args, str):
                args = args.split()

            if test_ns:
                result_ns = self.parser.parse_args(args)
                print(result_ns, expected_ns)
                assert result_ns != expected_ns
            else:
                raises = self.assertRaises
                raises(ArgumentParserError, self.parser.parse_args, args)

    def _test_dispatch_successes(self, successes):
        for args, expected_ns, expected_ret in successes:
            print(args)
            if isinstance(args, str):
                args = args.split()

            result_ns = self.parser.parse_args(args)
            print(result_ns, expected_ns)
            assert result_ns == expected_ns
            result_ret = self.parser.dispatch_commands()
            print(result_ret, expected_ret)
            assert result_ret == expected_ret


count = 0

class TestMainDispatch(BaseUnitTest):
    def test_1_blank(self):
        start_count = count

        @cmdify.main_command
        def m():
            global count
            count += 1
            return None

        failures = ['f', 'arg', '-f', '--f']

        successes = [
            ('', NS(), (None, None)),
            (' ', NS(), (None, None)),
        ]

        self._run_dispatch_tests(failures, successes)
        assert count == len(successes) + start_count

    def test_2_single_arg(self):
        start_count = count

        @cmdify.main_command
        def m(arg):
            global count
            count += 1
            assert arg == '5'
            return arg

        failures = ['f', 'arg', '-f', '--f', '--arg5']

        successes = [
            ('--arg 5', NS(arg='5'), ('5', None)),
            ('--arg=5', NS(arg='5'), ('5', None)),
        ]

        self._run_dispatch_tests(failures, successes)
        assert count == len(successes) + start_count

    def test_3_single_arg_with_default(self):
        start_count = count
        @cmdify.main_command
        def m(arg=5):
            global count
            count += 1
            return arg

        failures = ['f', 'arg', '-f', '--f', '--arg5', '--arg five', '--arg',
            '--arg=5.4',
            ('', NS(arg=6)),
            ('', NS(arg='5')),
            ('--arg=5', NS(arg='5')),
        ]

        successes = [
            ('', NS(arg=5), (5, None)),
            ('--arg=7', NS(arg=7), (7, None)),
            ('--arg 7', NS(arg=7), (7, None)),
            ('--arg=-7', NS(arg=-7), (-7, None)),
        ]

        self._run_dispatch_tests(failures, successes)
        assert count == len(successes) + start_count

    def test_4_single_arg_with_flag(self):
        start_count = count
        @cmdify.main_command(arg={'flag': '-a'})
        def m(arg):
            global count
            count += 1
            return arg

        failures = [' ', 'f', 'arg', '-f', '--f', '--arg5', '--arg', '-a',
            ('-a 7', NS(arg=7)),
            ('-a-999', NS(arg=-999)),
        ]

        successes = [
            ('--arg=5', NS(arg='5'), ('5', None)),
            ('--arg 7', NS(arg='7'), ('7', None)),
            ('--arg=-5', NS(arg='-5'), ('-5', None)),
            ('-a=5', NS(arg='5'), ('5', None)),
            ('-a7', NS(arg='7'), ('7', None)),
            ('-a -8', NS(arg='-8'), ('-8', None)),
            ('-a 999', NS(arg='999'), ('999', None)),
        ]

        self._run_dispatch_tests(failures, successes)
        assert count == len(successes) + start_count

    def test_5_single_arg_with_default_and_flag(self):
        start_count = count
        @cmdify.main_command(arg={'flag': '-a'})
        def m(arg=1234):
            global count
            count += 1
            return arg

        failures = ['f', 'arg', '-f', '--f', '--arg5', '--arg', '-a',
            ('-a 7', NS(arg='7')),
            ('-a9', NS(arg='9')),
        ]

        successes = [
            ('', NS(arg=1234), (1234, None)),
            ('--arg=5', NS(arg=5), (5, None)),
            ('--arg 7', NS(arg=7), (7, None)),
            ('--arg=-5', NS(arg=-5), (-5, None)),
            ('-a=5', NS(arg=5), (5, None)),
            ('-a7', NS(arg=7), (7, None)),
            ('-a -8', NS(arg=-8), (-8, None)),
            ('-a 999', NS(arg=999), (999, None)),
        ]

        self._run_dispatch_tests(failures, successes)
        assert count == len(successes) + start_count

    def test_6_single_arg_with_bool_false(self):
        start_count = count
        @cmdify.main_command
        def m(arg=False):
            global count
            count += 1
            return arg

        failures = ['f', 'arg', '-f', '--f', '--arg5', '-a',
            ('--arg', NS(arg=False)),
        ]

        successes = [
            ('', NS(arg=False), (False, None)),
            ('--arg', NS(arg=True), (True, None)),
        ]

        self._run_dispatch_tests(failures, successes)
        assert count == len(successes) + start_count

    def test_7_single_arg_with_bool_true(self):
        start_count = count
        @cmdify.main_command
        def m(arg=True):
            global count
            count += 1
            return arg

        failures = ['f', 'arg', '-f', '--f', '--arg5', '--arg', '-a',
            ('--not-arg', NS(arg=True)),
        ]

        successes = [
            ('', NS(arg=True), (True, None)),
            ('--not-arg', NS(arg=False), (False, None)),
        ]

        self._run_dispatch_tests(failures, successes)
        assert count == len(successes) + start_count
