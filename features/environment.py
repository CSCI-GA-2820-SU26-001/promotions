"""
Environment setup for BDD tests
"""

import requests
from os import getenv

BASE_URL = getenv("BASE_URL", "http://localhost:8080")
WAIT_SECONDS = int(getenv("WAIT_SECONDS", "60"))


def before_all(context):
    """Runs once before all features"""
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS


def before_scenario(context, scenario):
    """Runs before each scenario — clean the database"""
    context.resp = None
    requests.delete(f"{context.base_url}/promotions/reset")


def after_scenario(context, scenario):
    """Runs after each scenario"""
    pass
