Feature: App navigation menu
  Verify that navigation buttons correctly toggle page visibility

  Scenario: Navigate between Home, Dashboard, and Prediction pages
    Given the app is running
    Then only the Home page should be visible
    When the user clicks the "Dashboard" button
    Then only the Dashboard page should be visible
    When the user clicks the "Retour à l'accueil" button
    Then only the Home page should be visible
    When the user clicks the "Prediction" button
    Then only the Prediction page should be visible
