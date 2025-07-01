import unittest
import json
from server.app import app
from server.models import db, Plant

class PlantRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            # Seed with one plant
            plant = Plant(name="Aloe", image="./images/aloe.jpg", price=11.50, is_in_stock=True)
            db.session.add(plant)
            db.session.commit()
            self.plant_id = plant.id

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_patch_plant_success(self):
        update_data = {"is_in_stock": False}
        response = self.app.patch(f'/plants/{self.plant_id}',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], self.plant_id)
        self.assertEqual(data['is_in_stock'], False)

    def test_patch_plant_not_found(self):
        update_data = {"is_in_stock": False}
        response = self.app.patch('/plants/9999',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_delete_plant_success(self):
        response = self.app.delete(f'/plants/{self.plant_id}')
        self.assertEqual(response.status_code, 204)
        # Verify plant is deleted
        get_response = self.app.get(f'/plants/{self.plant_id}')
        self.assertEqual(get_response.status_code, 404)  # Plant not found after deletion

    def test_delete_plant_not_found(self):
        response = self.app.delete('/plants/9999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
