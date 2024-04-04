# In Ihrem Testmodul
import unittest
from unittest.mock import MagicMock
from app import app

class RanglisteTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.mock_cursor = MagicMock()
        self.mock_cursor.fetchall.return_value = [(1,"Spieler 1", 100), (2,"Spieler 2", 90)]
        self.mock_cursor.close.return_value = None
        self.mock_connection = MagicMock()
        self.mock_connection.cursor.return_value = self.mock_cursor

        # Mocken der MySQL-Erweiterung
        self.mock_mysql = MagicMock()
        self.mock_mysql.connection.cursor.return_value = self.mock_cursor

        # Mocken der MySQL-Erweiterung in der Flask-App
        app.mysql = self.mock_mysql

    def test_rangliste(self):
        print()

if __name__ == '__main__':
    unittest.main()
