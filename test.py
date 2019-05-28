import unittest
import os
from flask import Flask, request
app = Flask(__name__)
class BasicTest(unittest.TestCase):

	def setup(self):
		app.config['TESTING'] = True
		app.config['DEBUG'] = False
		self.app = app.test_client()

	def tearDown(self):
		pass

	def test_main_page(self):
		response = app.request.get('/', follow_redirects=True)
		self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
	unittest.main()