# test_rangliste.py
from mock import mock
import unittest

from app import create_app # Anpassen an Ihren App-Aufbau

app = create_app('testing')
class TestRangliste(unittest.TestCase):

  def setUp(self):
    self.app = app('testing')  # Erstelle Flask-Test-App
    self.app_context = self.app.app_context()
    self.app_context.push()  # Aktiviere App-Kontext

  def tearDown(self):
    self.app_context.pop()  # Beende App-Kontext

  @mock.patch('app.rangliste.cursor.execute')  # Mocke die cursor.execute Methode
  def test_rangliste_leere_tabelle(self, mock_execute):
    """
    Testet die Rangliste mit einer leeren Tabelle.
    """
    mock_execute.return_value = []
    with self.app.test_client() as client:
      response = client.get('/rangliste')  # Sende GET-Request an /rangliste
      self.assertEqual(response.status_code, 200)  # Prüfe Statuscode 200 (OK)
      self.assertEqual(response.json, [])  # Prüfe ob leere Liste zurückgegeben wird

  def test_rangliste_ein_eintrag(self, mock_execute):
    """
    Testet die Rangliste mit einem Eintrag.
    """
    mock_execute.return_value = [("Spieler 1", 100, 1)]
    with self.app.test_client() as client:
      response = client.get('/rangliste')
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json, [{"name": "Spieler 1", "punkte": 100, "platz": 1}])

  # ... weitere Testmethoden für verschiedene Szenarien

if __name__ == "__main__":
  unittest.main()
