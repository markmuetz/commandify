VERSION = (0, 0, 4, 0, 'alpha')


def get_version(form='short'):
    if form == 'short':
        return '.'.join([str(v) for v in VERSION[:4]])
    elif form == 'long':
        return '.'.join([str(v) for v in VERSION][:4]) + '-' + VERSION[4]
    else:
        raise ValueError('unrecognised form specifier: {0}'.format(form))


def compare_to_current_version(version_str, form='short'):
    version = parse_version(version_str, form)
    return compare_versions(version, VERSION)


def parse_version(version_str, form='short'):
    project_status = VERSION[4]

    if form == 'long':
        version_numbers_str, project_status = version_str.split('-')
    elif form == 'short':
        version_numbers_str = version_str
    else:
        raise ValueError('Unrecognised form specifier: {0}'.format(form))
    try:
        version_numbers = [int(n) for n in version_numbers_str.split('.')]
    except ValueError:
        raise ValueError('All version numbers must be integers: "{0}"'
                         .format(version_str))

    if len(version_numbers) != 4:
        raise ValueError('Wrong length of version string: "{0}"'
                         .format(version_str))

    return tuple(version_numbers) + (project_status, )


def compare_versions(version1, version2):
    if version1 == version2:
        return 0
    return 1 if version1[:4] > version2[:4] else -1


__version__ = get_version()


if __name__ == '__main__':
    print(get_version())
