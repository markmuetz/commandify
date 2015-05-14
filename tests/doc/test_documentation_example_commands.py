import inspect
import subprocess
import os

import commandify.commandify_examples as ce
import commandify as cmdify


def parse_doc_for_commands(doc):
    if not doc:
        return []
    cmds = []
    lines = doc.split('\n')
    usage_found = False
    for line in lines:
        if line[:10] == '    usage:':
            usage_found = True
        if usage_found:
            if line[:27] == '        commandify_examples':
                cmds.append(parse_command(line))
    return cmds


def parse_command(line):
    cmd = line[8:]
    return './{0}'.format(cmd)


class TestDocumentationExampleCommands(object):
    def __init__(self):
        pass

    def test_1_test_all_example_commands(self):
        """Test that example commands execute and give return code 0"""
        cmds = []
        for cmd, args, kwargs in cmdify._commands.values():
            cmds.extend(parse_doc_for_commands(cmd.__doc__))

        for cmd, args, kwargs in cmdify._main_commands.values():
            cmds.extend(parse_doc_for_commands(cmd.__doc__))

        cwd = os.getcwd()
        os.chdir('commandify')
        for cmd in cmds:
            print(cmd)
            ret = subprocess.call(cmd, shell=True)
            assert ret == 0
        os.chdir(cwd)
