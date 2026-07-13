"""
Step definitions for Promotions API BDD tests
"""

import json
import requests
from behave import given, when, then

# ---------------------------------------------------------------
# GIVEN steps
# ---------------------------------------------------------------


@given("the server is started")
def step_server_started(context):
    """Verify the server is reachable"""
    context.base_url = context.base_url
    response = requests.get(f"{context.base_url}/")
    assert response.status_code == 200, f"Server not running at {context.base_url}"


@given("the following promotions exist")
def step_promotions_exist(context):
    """Create promotions from a table in the feature file"""
    context.last_id = None
    for row in context.table:
        payload = {
            "name": row["name"],
            "promotion_type": row["promotion_type"],
            "discount_value": float(row["discount_value"]),
            "start_date": row["start_date"],
            "end_date": row["end_date"],
        }
        response = requests.post(
            f"{context.base_url}/promotions",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        assert (
            response.status_code == 201
        ), f"Failed to create promotion: {response.text}"
        context.last_id = response.json()["id"]


# ---------------------------------------------------------------
# WHEN steps
# ---------------------------------------------------------------


@when('I visit the "home page"')
def step_visit_home_page(context):
    """GET the root URL"""
    context.resp = requests.get(f"{context.base_url}/")


@when('I send a GET request to "{url}"')
def step_send_get(context, url):
    """Send a GET request"""
    context.resp = requests.get(f"{context.base_url}{url}")


@when("I send a GET request to the last created promotion")
def step_send_get_last(context):
    """Send a GET request to the last created promotion"""
    context.resp = requests.get(f"{context.base_url}/promotions/{context.last_id}")


@when("I send a PUT request to the last created promotion with body")
def step_send_put_last(context):
    """Send a PUT request to the last created promotion"""
    context.resp = requests.put(
        f"{context.base_url}/promotions/{context.last_id}",
        data=context.text,
        headers={"Content-Type": "application/json"},
    )


@when('I send a POST request to "{url}" with body')
def step_send_post_with_body(context, url):
    """Send a POST request with a JSON body"""
    context.resp = requests.post(
        f"{context.base_url}{url}",
        data=context.text,
        headers={"Content-Type": "application/json"},
    )


@when('I send a POST request to "{url}" with content type "{content_type}"')
def step_send_post_wrong_content_type(context, url, content_type):
    """Send a POST request with wrong content type"""
    context.resp = requests.post(
        f"{context.base_url}{url}",
        data="not json",
        headers={"Content-Type": content_type},
    )


@when('I send a PUT request to "{url}" with body')
def step_send_put_with_body(context, url):
    """Send a PUT request with a JSON body"""
    context.resp = requests.put(
        f"{context.base_url}{url}",
        data=context.text,
        headers={"Content-Type": "application/json"},
    )


@when('I send a DELETE request to "{url}"')
def step_send_delete(context, url):
    """Send a DELETE request"""
    context.resp = requests.delete(f"{context.base_url}{url}")


# ---------------------------------------------------------------
# THEN steps
# ---------------------------------------------------------------


@then("the response status code should be {status_code:d}")
def step_check_status_code(context, status_code):
    """Check the response status code"""
    assert (
        context.resp.status_code == status_code
    ), f"Expected {status_code}, got {context.resp.status_code}: {context.resp.text}"


@then('I should see "{text}"')
def step_should_see(context, text):
    """Check the response body contains text"""
    assert (
        text in context.resp.text
    ), f"Expected '{text}' in response: {context.resp.text}"


@then("the response should be an empty list")
def step_response_empty_list(context):
    """Check the response body is an empty list"""
    data = context.resp.json()
    assert data == [], f"Expected empty list, got: {data}"


@then("the response should contain {count:d} promotions")
def step_response_count(context, count):
    """Check the number of promotions in the response"""
    data = context.resp.json()
    assert len(data) == count, f"Expected {count} promotions, got {len(data)}"


@then('the response should contain a promotion with name "{name}"')
def step_response_contains_name(context, name):
    """Check the response contains a promotion with the given name"""
    data = context.resp.json()
    if isinstance(data, list):
        names = [p["name"] for p in data]
        assert name in names, f"Expected '{name}' in {names}"
    else:
        assert data["name"] == name, f"Expected name '{name}', got '{data['name']}'"


@then('the response header "{header}" should be set')
def step_response_header_set(context, header):
    """Check a response header is present"""
    assert (
        header in context.resp.headers
    ), f"Expected header '{header}' in {dict(context.resp.headers)}"


@then('the response should contain "{text}"')
def step_response_contains_text(context, text):
    """Check the response body contains the given text"""
    assert (
        text in context.resp.text
    ), f"Expected '{text}' in response: {context.resp.text}"
