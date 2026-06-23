######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
TestPromotion API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Promotion
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/promotions"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertIn("service", data)
        self.assertIn("version", data)
        self.assertIn("promotions_url", data)
        self.assertIn("/promotions", data["promotions_url"])

    def test_create_promotion(self):
        """It should create a promotion and return 201 with a Location header"""
        promotion = PromotionFactory()
        payload = promotion.serialize()
        payload.pop("id")  # id is assigned by the DB, not provided by the client

        resp = self.client.post(
            "/promotions",
            json=payload,
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("Location", resp.headers)

        data = resp.get_json()
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["name"], payload["name"])
        self.assertEqual(data["promotion_type"], payload["promotion_type"])
        self.assertEqual(data["discount_value"], str(payload["discount_value"]))
        self.assertEqual(data["start_date"], payload["start_date"])
        self.assertEqual(data["end_date"], payload["end_date"])

    def test_create_promotion_invalid_content_type(self):
        """It should return 415 when Content-Type is not application/json"""
        resp = self.client.post(
            "/promotions",
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_promotion_missing_required_field(self):
        """It should return 400 when required fields are missing"""
        resp = self.client.post(
            "/promotions",
            json={"discount_value": 10.0},  # missing name and promotion_type
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_invalid_promotion_type(self):
        """It should return 400 when promotion_type is not a valid enum value"""
        resp = self.client.post(
            "/promotions",
            json={
                "name": "Bad Type Promo",
                "promotion_type": "INVALID_TYPE",
                "discount_value": 5.0,
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_promotion(self):
        """It should delete a Promotion"""
        promotion = PromotionFactory()
        promotion.create()

        resp = self.client.delete(f"/promotions/{promotion.id}")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(resp.data, b"")
        self.assertIsNone(Promotion.find(promotion.id))

    def test_delete_promotion_not_found(self):
        """It should return no content when deleting a missing Promotion"""
        resp = self.client.delete("/promotions/0")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(resp.data, b"")

    def test_read_promotion(self):
        """It should read a single Promotion"""
        promotion = PromotionFactory()
        promotion.create()

        resp = self.client.get(f"/promotions/{promotion.id}")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], promotion.id)
        self.assertEqual(data["name"], promotion.name)
        self.assertEqual(data["promotion_type"], promotion.promotion_type.name)
        self.assertEqual(data["start_date"], promotion.start_date.isoformat())
        self.assertEqual(data["end_date"], promotion.end_date.isoformat())

    def test_read_promotion_not_found(self):
        """It should not read a Promotion that does not exist"""
        resp = self.client.get("/promotions/0")

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = resp.get_json()
        self.assertEqual(data["status"], status.HTTP_404_NOT_FOUND)
        self.assertEqual(data["error"], "Not Found")

    def test_get_promotion_list(self):
        """It should return a list of all Promotions"""
        promotions = PromotionFactory.create_batch(5)
        for promotion in promotions:
            promotion.create()

        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_promotion_list_when_empty(self):
        """It should return an empty list when no Promotions exist"""
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data, [])

    def test_get_promotion_list_returns_correct_fields(self):
        """It should return Promotions with all expected fields"""
        promotion = PromotionFactory()
        promotion.create()

        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)

        result = data[0]
        self.assertEqual(result["name"], promotion.name)
        self.assertEqual(result["promotion_type"], promotion.promotion_type.name)
        self.assertEqual(
            float(result["discount_value"]), float(promotion.discount_value)
        )
        self.assertEqual(result["start_date"], promotion.start_date.isoformat())
        self.assertEqual(result["end_date"], promotion.end_date.isoformat())
        self.assertIn("id", result)

    def test_update_promotion(self):
        """It should update an existing Promotion"""
        promotion = PromotionFactory()
        promotion.create()

        new_data = promotion.serialize()
        new_data["name"] = "Updated Promo Name"
        new_data["discount_value"] = "25.00"
        new_data["end_date"] = "2026-12-31"

        resp = self.client.put(
            f"{BASE_URL}/{promotion.id}",
            json=new_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["id"], promotion.id)
        self.assertEqual(data["name"], "Updated Promo Name")
        self.assertEqual(float(data["discount_value"]), 25.00)
        self.assertEqual(data["end_date"], "2026-12-31")

    def test_update_promotion_persists_to_database(self):
        """It should persist the updated fields after a PUT"""
        promotion = PromotionFactory()
        promotion.create()

        new_data = promotion.serialize()
        new_data["name"] = "Persisted Name"

        resp = self.client.put(
            f"{BASE_URL}/{promotion.id}",
            json=new_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.client.get(f"{BASE_URL}/{promotion.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["name"], "Persisted Name")

    def test_update_promotion_not_found(self):
        """It should return 404 when updating a Promotion that does not exist"""
        promotion = PromotionFactory()
        new_data = promotion.serialize()
        new_data.pop("id")

        resp = self.client.put(
            f"{BASE_URL}/0",
            json=new_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        data = resp.get_json()
        self.assertIn("status", data)
        self.assertIn("error", data)
        self.assertIn("message", data)
        self.assertEqual(data["status"], status.HTTP_404_NOT_FOUND)
        self.assertEqual(data["error"], "Not Found")

    def test_update_promotion_missing_required_field(self):
        """It should return 400 when the update payload is missing required fields"""
        promotion = PromotionFactory()
        promotion.create()

        resp = self.client.put(
            f"{BASE_URL}/{promotion.id}",
            json={"discount_value": "10.00"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_promotion_invalid_content_type(self):
        """It should return 415 when Content-Type is not application/json"""
        promotion = PromotionFactory()
        promotion.create()

        resp = self.client.put(
            f"{BASE_URL}/{promotion.id}",
            data="not json",
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_promotion_does_not_change_id(self):
        """It should not allow the promotion id to be changed via the payload"""
        promotion = PromotionFactory()
        promotion.create()
        original_id = promotion.id

        new_data = promotion.serialize()
        new_data["id"] = original_id + 9999

        resp = self.client.put(
            f"{BASE_URL}/{original_id}",
            json=new_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["id"], original_id)

    def test_method_not_allowed(self):
        """It should return 405 when an unsupported HTTP method is used"""
        resp = self.client.delete(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = resp.get_json()
        self.assertIn("status", data)
        self.assertIn("error", data)
        self.assertIn("message", data)
        self.assertEqual(data["status"], status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(data["error"], "Method not Allowed")
