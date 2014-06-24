# Copyright (c) 2013, Kevin Greenan (kmgreen2@gmail.com)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.  THIS SOFTWARE IS
# PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
# NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from functools import wraps
import os
import sys
import unittest


run_under_valgrind = False
test_cmd_prefix = ""
log_filename_prefix = ""


# skipUnless added in Python 2.7;
try:
    from unittest import skipUnless
except ImportError:
    def skipUnless(condition, message):
        def decorator(testfunc):
            @wraps(testfunc)
            def wrapper(self):
                if condition:
                    testfunc(self)
                else:
                    print "Skipping", testfunc.__name__, "--", message
            return wrapper
        return decorator


#
# TestCoreC Test Configuration
#
xor_code_test = "test_xor_hd_code"
alg_sig_test = "alg_sig_test"
c_tests = [
    xor_code_test,
    alg_sig_test,
]


def SearchPath(name, path=None, exts=('',)):
    """Search PATH for a binary.

    Args:
      name: the filename to search for
      path: the optional path string (default: os.environ['PATH')
      exts: optional list/tuple of extensions to try (default: ('',))

    Returns:
      The abspath to the binary or None if not found.
    """
    path = path or os.environ['PATH']
    for dir in path.split(os.pathsep):
        for ext in exts:
            binpath = os.path.join(dir, name) + ext
            if os.path.exists(binpath):
                return os.path.abspath(binpath)
    return None


def valid_c_tests():
    """
    Asserts that the c_tests are reachable.  Returns True if all of the
    tests exists as a file, False otherwise.
    """
    valid = True

    for test in c_tests:
        if SearchPath(test) is None:
            valid = False

    return valid


class TestCoreC(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @skipUnless(valid_c_tests(), "Error locating tests in: %s" % c_tests)
    def test_c_stuff(self):
        for test in c_tests:
            self.assertEqual(0, os.system(test))


class TestCoreValgrind(unittest.TestCase):

    def __init__(self, *args):
        self.pyeclib_core_test = "test_pyeclib_c.py"
        self.pyeclib_iface_test = "test_pyeclib_api.py"

        unittest.TestCase.__init__(self, *args)

    def setUp(self):
        # Determine which directory we're in
        dirs = os.getcwd().split('/')
        if dirs[-1] == 'test':
            self.pyeclib_test_dir = "."
        else:
            self.pyeclib_test_dir = "./test"

        # Create the array of tests to run
        self.py_test_dirs = [
            (self.pyeclib_test_dir, self.pyeclib_core_test),
            (self.pyeclib_test_dir, self.pyeclib_iface_test)
        ]

    def tearDown(self):
        pass

    def test_core_valgrind(self):
        self.assertTrue(True)
        cur_dir = os.getcwd()
        print("\n")
        for (dir, test) in self.py_test_dirs:
            sys.stdout.write("Running test %s ... " % test)
            sys.stdout.flush()
            os.chdir(dir)
            if os.path.isfile(test):
                ret = os.system(
                    "%s python %s >%s/%s.%s.out 2>&1" %
                    (test_cmd_prefix, test, cur_dir,
                     log_filename_prefix, test))

                self.assertEqual(0, ret)
                os.system("rm -f *.pyc")
                os.chdir(cur_dir)
                print('ok')
            else:
                self.assertTrue(False)
                print('failed')


if __name__ == "__main__":
    if '_valgrind' in sys.argv[0]:
        if (0 != os.system("which valgrind")):
            print("You don't appear to have 'valgrind' installed")
            sys.exit(-1)
        run_under_valgrind = True
        test_cmd_prefix = "valgrind --leak-check=full "
        log_filename_prefix = "valgrind"
    unittest.main(verbosity=2)
