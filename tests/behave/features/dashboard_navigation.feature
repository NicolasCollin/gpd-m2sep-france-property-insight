Feature: Dashboard navigation
  As a user
  I want to switch between Overview and Data visualization
  So that I can explore different parts of the dashboard

  Scenario: View Overview tab
    When the user opens the "Overview" tab
    Then the "Overview" tab should be visible

  Scenario: View Data visualization tab
    When the user opens the "Data visualization" tab
    Then the "Data visualization" tab should be visible
