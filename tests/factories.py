"""
Test Factory to make fake objects for testing
"""

from datetime import timedelta
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from service.models import Promotion, PromotionType


class PromotionFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Promotion

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")

    promotion_type = FuzzyChoice(list(PromotionType))
    discount_value = FuzzyDecimal(0, 100, precision=2)
    start_date = factory.Faker("date_object")
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=7))
    active = True
