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
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Promotion, PromotionType, DataValidationError, db
from .factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Promotion   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestPromotion(TestCase):
    """Test Cases for Promotion Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

        # add new db columns
        db.drop_all()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_promotion_types_members(self):
        """It should have the defined PromotionType members"""
        self.assertIn(PromotionType.UNKNOWN, PromotionType)
        self.assertIn(PromotionType.PERCENT_OFF, PromotionType)
        self.assertIn(PromotionType.FIXED_AMOUNT, PromotionType)
        self.assertIn(PromotionType.BOGO, PromotionType)

    def test_create_promotion(self):
        """It should create a promotion that persists in the database"""
        resource = PromotionFactory()
        resource.create()
        self.assertIsNotNone(resource.id)
        found = Promotion.all()
        self.assertEqual(len(found), 1)
        data = Promotion.find(resource.id)
        self.assertEqual(data.name, resource.name)

    def test_create_promotion_with_type(self):
        """It should create a promotion with a specific PromotionType value"""
        resource = PromotionFactory(promotion_type=PromotionType.PERCENT_OFF)
        resource.create()
        found = Promotion.find(resource.id)
        self.assertEqual(found.promotion_type, PromotionType.PERCENT_OFF)

    def test_create_db_error_raises_data_validation_error(self):
        """It should raise DataValidationError and rollback when db.session.add fails"""
        resource = PromotionFactory()
        with patch(
            "service.models.db.session.commit", side_effect=Exception("DB error")
        ):
            with self.assertRaises(DataValidationError):
                resource.create()

    def test_update_db_error_raises_data_validation_error(self):
        """It should raise DataValidationError and rollback when db.session.commit fails on update"""
        resource = PromotionFactory()
        resource.create()
        resource.name = "Changed"
        with patch(
            "service.models.db.session.commit", side_effect=Exception("DB error")
        ):
            with self.assertRaises(DataValidationError):
                resource.update()

    def test_delete_promotion(self):
        """It should delete a promotion and remove it from the database"""
        resource = PromotionFactory()
        resource.create()
        self.assertEqual(len(Promotion.all()), 1)
        resource.delete()
        self.assertEqual(len(Promotion.all()), 0)
        self.assertIsNone(Promotion.find(resource.id))

    def test_delete_db_error_raises_data_validation_error(self):
        """It should raise DataValidationError and rollback when db.session.delete fails"""
        resource = PromotionFactory()
        resource.create()
        with patch(
            "service.models.db.session.delete", side_effect=Exception("DB error")
        ):
            with self.assertRaises(DataValidationError):
                resource.delete()

    # Serialization ------------
    def test_serialize_promotion(self):
        """It should correctly serialize all fields of a promotion"""
        resource = PromotionFactory(promotion_type=PromotionType.FIXED_AMOUNT)
        resource.create()
        data = resource.serialize()
        self.assertEqual(data["id"], resource.id)
        self.assertEqual(data["name"], resource.name)
        self.assertEqual(data["promotion_type"], PromotionType.FIXED_AMOUNT.name)
        self.assertEqual(data["discount_value"], resource.discount_value)
        self.assertEqual(data["start_date"], resource.start_date.isoformat())
        self.assertEqual(data["end_date"], resource.end_date.isoformat())

    def test_deserialize_promotion(self):
        """It should correctly deserialize a promotion from a dictionary"""
        resource = PromotionFactory(promotion_type=PromotionType.FIXED_AMOUNT)
        resource.create()
        serialized = resource.serialize()
        new_promotion = Promotion()
        new_promotion.deserialize(serialized)
        self.assertEqual(new_promotion.name, resource.name)
        self.assertEqual(new_promotion.promotion_type, resource.promotion_type)
        self.assertEqual(new_promotion.discount_value, resource.discount_value)
        self.assertEqual(new_promotion.start_date, resource.start_date)
        self.assertEqual(new_promotion.end_date, resource.end_date)

    def test_deserialize_missing_field(self):
        """It should raise DataValidationError when a required field is missing"""
        promotion = Promotion()
        with self.assertRaises(DataValidationError):
            promotion.deserialize({"promotion_type": "UNKNOWN"})
        with self.assertRaises(DataValidationError):
            promotion.deserialize({"name": "Test Promotion"})

    def test_deserialize_invalid_attribute_raises_data_validation_error(self):
        """It should raise DataValidationError for invalid attribute types"""
        promotion = Promotion()
        with self.assertRaises(DataValidationError):
            promotion.deserialize(None)

    def test_find_by_name_returns_empty_when_no_match(self):
        """It should return no results when no promotion matches the name"""
        PromotionFactory(name="Test Name").create()
        results = Promotion.find_by_name("Nonexistent")
        self.assertEqual(results.count(), 0)

    def test_find_by_type(self):
        """It should find Promotions by promotion_type"""
        promotion = PromotionFactory(promotion_type=PromotionType.BOGO)
        promotion.create()
        other = PromotionFactory(promotion_type=PromotionType.PERCENT_OFF)
        other.create()

        found = Promotion.find_by_type(PromotionType.BOGO).all()
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].promotion_type, PromotionType.BOGO)

    def test_find_by_type_multiple_matches(self):
        """It should return all Promotions matching the given promotion_type"""
        for _ in range(3):
            promotion = PromotionFactory(promotion_type=PromotionType.BOGO)
            promotion.create()
        other = PromotionFactory(promotion_type=PromotionType.FIXED_AMOUNT)
        other.create()

        found = Promotion.find_by_type(PromotionType.BOGO).all()
        self.assertEqual(len(found), 3)
        for promotion in found:
            self.assertEqual(promotion.promotion_type, PromotionType.BOGO)

    def test_find_by_type_not_found(self):
        """It should return an empty list when no Promotions match the type"""
        promotion = PromotionFactory(promotion_type=PromotionType.PERCENT_OFF)
        promotion.create()

        found = Promotion.find_by_type(PromotionType.BOGO).all()
        self.assertEqual(found, [])

    def test_find_by_type_empty_database(self):
        """It should return an empty list when there are no Promotions at all"""
        found = Promotion.find_by_type(PromotionType.BOGO).all()
        self.assertEqual(found, [])

    def test_active_defaults_to_true(self):
        """It should default active to True when not specified"""
        promotion = PromotionFactory()
        promotion.create()
        found = Promotion.find(promotion.id)
        self.assertTrue(found.active)

    def test_serialize_includes_active(self):
        """It should include active in the serialized output"""
        promotion = PromotionFactory(active=False)
        promotion.create()
        data = promotion.serialize()
        self.assertIn("active", data)
        self.assertFalse(data["active"])

    def test_deserialize_active_field(self):
        """It should deserialize the active field correctly"""
        promotion = PromotionFactory(active=True)
        promotion.create()
        serialized = promotion.serialize()
        serialized["active"] = False
        new_promotion = Promotion()
        new_promotion.deserialize(serialized)
        self.assertFalse(new_promotion.active)
