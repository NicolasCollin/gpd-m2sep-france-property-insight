Feature: Property price prediction (logic level)
  As a user
  I want to estimate the price of a property
  So that I get an immediate prediction from the model

  Scenario: Run a valid prediction
    When I run a prediction with valid property data
      | postal | prop_type | area | rooms | land |
      | 75001  |  House    | 80   | 3     | 50   |
    Then the result should contain "Estimated property price"

  Scenario: Run a prediction with invalid data
    When I run a prediction with invalid property data
      | postal | prop_type | area | rooms | land |
      | abc    | House     | -1   | 0     | -5   |
    Then the result should contain "error" or "failed"
