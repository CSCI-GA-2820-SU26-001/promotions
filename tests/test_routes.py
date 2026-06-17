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
