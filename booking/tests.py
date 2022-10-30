from django.test import TestCase
from datetime import datetime

import logging


class Tests(TestCase):

    def test_test(self):
        sec = datetime.now().second
        logging.debug(f"Current sec: {sec} is odd {bool(sec & 1)}")
        self.assertIs(bool(sec & 1), False)
