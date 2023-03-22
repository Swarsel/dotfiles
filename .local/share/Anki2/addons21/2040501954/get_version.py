"""
Parses Anki's version. Uncommment and run this directly to evaluate test cases.
"""

import re
from anki import version

""" Constants (reverse chronological order) """

ANKI_VER_LATEST = 0
ANKI_VER_PRE_2_1_41 = -1
ANKI_VER_PRE_2_1_0 = -2

""" Parsing """

def _parse_anki_version(version):
    try:
        v = tuple(map(int, re.match("(\d+)\.(\d+)\.(\d+)", version).groups()))

        if v[0] < 2:
            return ANKI_VER_PRE_2_1_0
        elif v[0] == 2 and v[1] < 1:
            return ANKI_VER_PRE_2_1_0
        elif v[0] == 2 and v[1] == 1 and v[2] < 41:
            return ANKI_VER_PRE_2_1_41
        else:
            return ANKI_VER_LATEST
    except:
        return ANKI_VER_LATEST

def get_anki_version():
    return _parse_anki_version(version)

""" Test Cases """

# def _test_version_parsing(version, expected):
#     if _parse_anki_version(version) == expected:
#         result = 'Passed'
#     else:
#         result = 'FAILED'
#     print("%s '%s'" % (result, version))

# _test_version_parsing('1.9.9', ANKI_VER_PRE_2_1_0)
# _test_version_parsing('2.0.31', ANKI_VER_PRE_2_1_0)
# _test_version_parsing('2.1.0', ANKI_VER_PRE_2_1_41)
# _test_version_parsing('2.1.4', ANKI_VER_PRE_2_1_41)
# _test_version_parsing('2.1.40', ANKI_VER_PRE_2_1_41)
# _test_version_parsing('2.1.40-beta', ANKI_VER_PRE_2_1_41)
# _test_version_parsing('2.1.41', ANKI_VER_LATEST)
# _test_version_parsing('2.1.41-beta', ANKI_VER_LATEST)
# _test_version_parsing('2.2.0', ANKI_VER_LATEST)
# _test_version_parsing('3.0.0', ANKI_VER_LATEST)
# _test_version_parsing('1.0', ANKI_VER_LATEST)
# _test_version_parsing('12345', ANKI_VER_LATEST)
# _test_version_parsing('abcde', ANKI_VER_LATEST)
