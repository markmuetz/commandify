Commandify
==========

Allows simple creation of Python command line utilities through decorating functions.

Installation
============

::

    pip install commandify

Running example and usage
=========================

Once commandify has been installed, it can be run with:

::

    commandify_examples --help


``commandify_examples`` code:

.. code:: python
    
    #!/usr/bin/env python
    '''Examples of a simple set of functions that use commandify
        usage::

            commandify_examples --help
            commandify_examples <command> --help
            commandify_examples --main-arg=22 <command>
            commandify_examples -m=22 <command>
            commandify_examples cmd_no_args

    '''
    from commandify import commandify, command, main_command


    @main_command(main_arg={'flag': '-m'})
    def main(main_arg=345):
        '''Example of how to use commandify
        Main command, called before any other command
        Can be used to set any global variables before any other commands executed.
        usage::

            commandify_examples --help
            commandify_examples --main-arg=22 cmd_no_args
            commandify_examples -m=22 cmd_no_args
            commandify_examples cmd_no_args

        '''
        print(type(main_arg))
        print("Main command: {0}".format(main_arg))


    @command
    def cmd_no_args():
        '''Simplest command
        usage::

            commandify_examples cmd_no_args

        '''
        print('cmd_no_args called')


    @command
    def cmd1(name):
        '''Simple command with argument
        usage::

            commandify_examples cmd1 --name=a1
            commandify_examples cmd1 --name a3
            commandify_examples cmd1 --name 'a4'

        '''
        print('cmd1 running')
        print(name)


    @command(username={'flag': '-n'})
    def cmd2(username, userid):
        '''Command with 2 args and a short flag set for name
        usage::

            commandify_examples cmd2 --username=steve --userid=55
            commandify_examples cmd2 -n=sarah --userid=56

        '''
        print('{0}: {1}'.format(userid, username))


    @command(some_arg={'default': 377})
    def cmd3(some_arg, arg_with_default='arg_default'):
        '''Command with defaults set in two ways
        first through decorator and second through function arguments.
        usage::

            commandify_examples cmd3
            commandify_examples cmd3 --arg-with-default=default_overridden

        '''
        # Type of some_arg will be int:
        print(type(some_arg))
        print(some_arg, arg_with_default)


    @command
    def cmd4(some_arg=False):
        '''Command with False bool default
        usage::

            commandify_examples cmd4
            commandify_examples cmd4 --some-arg

        '''
        # Type of some_arg will be bool:
        print(type(some_arg))
        print(some_arg)


    @command
    def cmd5(some_arg=True):
        '''Command with True bool default
        Command line argument gets turned into negative to handle this.
        usage::

            commandify_examples cmd5
            commandify_examples cmd5 --not-some-arg

        '''
        # Type of some_arg will be bool:
        print(type(some_arg))
        # If it is called without specifying --not-some-arg, it will be True.
        print(some_arg)


    @command
    def cmd6():
        print('cmd6 called')


    if __name__ == '__main__':
        commandify(suppress_warnings=['default_true'])
