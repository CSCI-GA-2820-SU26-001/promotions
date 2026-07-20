Feature: Promotions API
  As a store manager
  I need a RESTful catalogue service
  So that I can keep track of all my promotions

  Background:
    Given the following promotions
    | name         | promotion_type | discount_value | start_date | end_date   |
    | Summer Sale  | PERCENT_OFF    | 20.00          | 2026-06-01 | 2026-08-31 |
    | Black Friday | FIXED_AMOUNT   | 50.00          | 2026-11-27 | 2026-11-30 |

  # ---------------------------------------------------------------
  # Root / Service Discovery
  # ---------------------------------------------------------------

  Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotions Service" in the title
    And I should not see "404 Not Found"

  # ---------------------------------------------------------------
  # List Promotions
  # ---------------------------------------------------------------

  Scenario: List all promotions when none exist
    Given there are no promotions
    When I visit the "Home Page"
    And I press the "List" button
    Then I should see the message "No promotions found"
    And I should see 0 rows in the results table

  Scenario: List all promotions
    When I visit the "Home Page"
    And I press the "List" button
    Then I should see the message "Success"
    And I should see 2 rows in the results table
    And I should see "Summer Sale" in the results
    And I should see "Black Friday" in the results
  # ---------------------------------------------------------------
  # Create Promotion
  # ---------------------------------------------------------------

  Scenario: Create a new promotion
    When I visit the "Home Page"
    And I set the "Name" to "July Sale"
    And I select "Percent Off" in the "Type" dropdown
    And I set the "Discount Value" to "10.00"
    And I set the "Start Date" to "07-1-2026"
    And I set the "End Date" to "07-31-2026"
    And I press the "Create" button
    Then I should see the message "Promotion has been Created!"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And I should see "Unknown" in the "Type" dropdown
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Promotion has been Created!"
    And I should see "July Sale" in the "Name" field
    And I should see "Percent Off" in the "Type" dropdown
    And I should see "10.00" in the "Discount Value" field
    And I should see "2026-07-01" in the "Start Date" field
    And I should see "2026-07-31" in the "End Date" field

  # ---------------------------------------------------------------
  # Read Promotion
  # ---------------------------------------------------------------

  @wip
  Scenario: Read an existing promotion
    Given the following promotions exist
      | name        | promotion_type | discount_value | start_date | end_date   |
      | Summer Sale | PERCENT_OFF    | 20.00          | 2026-06-01 | 2026-08-31 |
    When I visit the "Home Page"
    And I set the "Promotion ID" to the last created promotion ID
    And I press the "Retrieve" button
    Then I should see "Summer Sale" in the "Name" field
    And I should see "PERCENT_OFF" in the "Type" dropdown
    And I should see the message "Success"

  @wip
  Scenario: Read a promotion that does not exist
    When I visit the "Home Page"
    And I set the "Promotion ID" to "0"
    And I press the "Retrieve" button
    Then I should see the message "Not Found"

  # ---------------------------------------------------------------
  # Update Promotion
  # ---------------------------------------------------------------

  @wip
  Scenario: Update an existing promotion
    Given the following promotions exist
      | name        | promotion_type | discount_value | start_date | end_date   |
      | Summer Sale | PERCENT_OFF    | 20.00          | 2026-06-01 | 2026-08-31 |
    When I visit the "Home Page"
    And I set the "Promotion ID" to the last created promotion ID
    And I press the "Retrieve" button
    And I set the "Name" to "Summer Sale Extended"
    And I set the "Discount Value" to "25.00"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I set the "Promotion ID" to the last created promotion ID
    And I press the "Retrieve" button
    Then I should see "Summer Sale Extended" in the "Name" field
    And I should see "25.00" in the "Discount Value" field

  @wip
  Scenario: Update a promotion that does not exist
    When I visit the "Home Page"
    And I set the "Promotion ID" to "0"
    And I set the "Name" to "Ghost Promo"
    And I press the "Update" button
    Then I should see the message "Not Found"

  # ---------------------------------------------------------------
  # Delete Promotion
  # ---------------------------------------------------------------

  @wip
  Scenario: Delete a promotion
    Given the following promotions exist
      | name        | promotion_type | discount_value | start_date | end_date   |
      | Summer Sale | PERCENT_OFF    | 20.00          | 2026-06-01 | 2026-08-31 |
    When I visit the "Home Page"
    And I set the "Promotion ID" to the last created promotion ID
    And I press the "Delete" button
    Then I should see the message "Promotion has been Deleted!"
    When I press the "Clear" button
    And I set the "Promotion ID" to the last created promotion ID
    And I press the "Retrieve" button
    Then I should see the message "Not Found"


  Given the following promotions
      | name        | promotion_type | discount_value | start_date | end_date   |
      | Summer Sale | PERCENT_OFF    | 20.00          | 2026-06-01 | 2026-08-31 |

  Scenario: Deactivate a promotion by searching by name
    When I visit the "Home Page"
    And I set the "Name" to "Summer Sale"
    And I press the "Search" button
    Then I should see "Summer Sale" in the results
    When I set the "Promotion ID" to the last created promotion ID
    And I press the "Deactivate" button
    Then I should see the message "Success"
    And I should see "false" in the results

  Scenario: Deactivate a promotion by retrieving by ID
    When I visit the "Home Page"
    And I set the "Promotion ID" to the last created promotion ID
    And I press the "Retrieve" button
    Then I should see the message "Success"
    When I press the "Deactivate" button
    Then I should see the message "Success"
    When I press the "Retrieve" button
    Then I should see "false" in the results