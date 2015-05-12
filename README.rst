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
    '''Top level documentation will be used for command line description'''
    from commandify import commandify, command, main_command
    
    
    @main_command(main_arg={'flag': '-m', 'type': int})
    def main(main_arg=345):
        '''./commandify_examples [options]
        Main command, called before any other command
        Can be used to set any global variables before any other commands executed.
        usage::
    
            ./commandify_examples --help
            ./commandify_examples <command> --help
            ./commandify_examples --main-arg=22 <command>
            ./commandify_examples -m=22 <command>
            ./commandify_examples cmd_no_args
    
        '''
        print("Main command: {0}".format(main_arg))
    
    
    @command
    def cmd_no_args():
        '''Simplest command
        usage::
    
            ./commandify_examples cmd_no_args
    
        '''
        print('cmd_no_args called')
    
    
    @command
    def cmd1(name):
        '''Simple command with argument
        usage::
    
            ./commandify_examples cmd1 --name=a1
            ./commandify_examples cmd1 --namea2
            ./commandify_examples cmd1 --name a3
            ./commandify_examples cmd1 --name 'a4'
    
        '''
        print('cmd1 running')
        print(name)
    
    
    @command(username={'flag': '-n'})
    def cmd2(username, userid):
        '''Command with 2 args and a short flag set for name
        usage::
    
            ./commandify_examples cmd2 --username=steve --userid=55
            ./commandify_examples cmd2 -n=sarah --userid=56
    
        '''
        print('{0}: {1}'.format(id, name))
    
    
    @command(some_arg={'default': 377})
    def cmd3(some_arg, arg_with_default='arg_default'):
        '''Command with defaults set in two ways
        first through decorator and second through function arguments.
        usage::
    
            ./commandify_examples cmd3
            ./commandify_examples cmd3 --arg-with-default=default_overridden
    
        '''
        print(some_arg, arg_with_default)
    
    
    @command
    def cmd4():
        print('cmd4 called')
    
    
    if __name__ == '__main__':
        commandify()
        
    
