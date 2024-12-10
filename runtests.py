#!/usr/bin/env python

"""
This suite runs tests in django environment. See:
https://docs.djangoproject.com/en/1.11/topics/testing/advanced/#using-the-django-test-runner-to-test-reusable-applications
"""

import os
import sys
import unittest

if __name__ == "__main__":
    print('Python: ', sys.version)

    dirname = os.path.abspath(os.path.dirname(__file__))
    sys.path.extend([dirname, "%s/src" % dirname, ])

    unittest.main()
