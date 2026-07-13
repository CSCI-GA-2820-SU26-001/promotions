Feature: Promotions API
  As a store manager
  I need to manage promotions
  So that I can offer discounts to customers

  Background:
    Given the server is started

  # ---------------------------------------------------------------
  # Root / Service Discovery
  # ---------------------------------------------------------------

  Scenario: The server is running
    When I visit the "home page"
    Then I should see "Promotions Service"
    And I should see "promotions_url"
    And the response status code should be 200

  # ---------------------------------------------------------------
  # List Promotions
  # ---------------------------------------------------------------

  Scenario: List all promotions when none exist
    When I send a GET request to "/promotions"
    Then the response status code should be 200
    And the response should be an empty list

  Scenario: List all promotions
    Given the following promotions exist
      | name         | promotion_type | discount_value | start_date | end_date   |
      | Summer Sale  | PERCENT_OFF    | 20.00          | 2026-06-01 | 2026-08-31 |
      | Black Friday | FIXED_AMOUNT   | 50.00          | 2026-11-27 | 2026-11-30 |
    When I send a GET request to "/promotions"
    Then the response status code should be 200
    And the response should contain 2 promotions
    And the response should contain a promotion with name "Summer Sale"
    And the response should contain a promotion with name "Black Friday"

  # ---------------------------------------------------------------
  # Create Promotion
  # ---------------------------------------------------------------

  Scenario: Create a new promotion
    When I send a POST request to "/promotions" with body
      """
      {
        "name": "Flash Sale",
        "promotion_type": "PERCENT_OFF",
        "discount_value": 15.00,
        "start_date": "2026-07-01",
        "end_date": "2026-07-07"
      }
      """
    Then the response status code should be 201
    And the response should contain a promotion with name "Flash Sale"
    And the response header "Location" should be set

  Scenario: Create a promotion with missing required fields
    When I send a POST request to "/promotions" with body
      """
      {
        "discount_value": 10.00
      }
      """
    Then the response status code should be 400

  Scenario: Create a promotion with wrong content type
    When I send a POST request to "/promotions" with content type "text/plain"
    Then the response status code should be 415

  # ---------------------------------------------------------------
  # Read Promotion
  # ---------------------------------------------------------------

  Scenario: Read an existing promotion
    Given the following promotions exist
      | name        | promotion_type | discount_value | start_date | end_date   |
      | Summer Sale | PERCENT_OFF    | 20.00          | 2026-06-01 | 2026-08-31 |
    When I send a GET request to the last created promotion
    Then the response status code should be 200
    And the response should contain a promotion with name "Summer Sale"

  Scenario: Read a promotion that does not exist
    When I send a GET request to "/promotions/0"
    Then the response status code should be 404
    And the response should contain "Not Found"

  # ---------------------------------------------------------------
  # Update Promotion
  # ---------------------------------------------------------------

  Scenario: Update an existing promotion
    Given the following promotions exist
      | name        | promotion_type | discount_value | start_date | end_date   |
      | Summer Sale | PERCENT_OFF    | 20.00          | 2026-06-01 | 2026-08-31 |
    When I send a PUT request to the last created promotion with body
      """
      {
        "name": "Summer Sale Extended",
        "promotion_type": "PERCENT_OFF",
        "discount_value": 25.00,
        "start_date": "2026-06-01",
        "end_date": "2026-09-30"
      }
      """
    Then the response status code should be 200
    And the response should contain a promotion with name "Summer Sale Extended"

  Scenario: Update a promotion that does not exist
    When I send a PUT request to "/promotions/0" with body
      """
      {
        "name": "Ghost Promo",
        "promotion_type": "BOGO",
        "discount_value": 0.00,
        "start_date": "2026-01-01",
        "end_date": "2026-01-02"
      }
      """
    Then the response status code should be 404

  # ---------------------------------------------------------------
  # Method Not Allowed
  # ---------------------------------------------------------------

  Scenario: Delete on collection returns method not allowed
    When I send a DELETE request to "/promotions"
    Then the response status code should be 405
