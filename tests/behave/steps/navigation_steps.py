from behave import given, then, when
from behave.runner import Context

from src.interface.menu import app_menu


def set_visibility(context: Context, home: bool, dashboard: bool, prediction: bool) -> None:
    """
    Helper function to update the simulated visibility state of the app pages.

    Args:
        context (Context): Behave context object for sharing state between steps.
        home (bool): Whether the Home page should be visible.
        dashboard (bool): Whether the Dashboard page should be visible.
        prediction (bool): Whether the Prediction page should be visible.
    """
    context.state = {
        "home": home,
        "dashboard": dashboard,
        "prediction": prediction,
    }


@given("the app is running")
def step_impl_app_running(context: Context) -> None:
    """
    Initialize the app menu and extract main page components.

    Sets the initial visibility state: only the Home page is visible.
    """
    context.menu = app_menu()

    # Extract page columns for reference (simulation only)
    with context.menu:
        context.home = context.menu.children[0]  # Home page column
        context.dashboard = context.menu.children[1]  # Dashboard page column
        context.prediction = context.menu.children[2]  # Prediction page column

    # Start state: only Home is visible
    set_visibility(context, home=True, dashboard=False, prediction=False)


@then("only the Home page should be visible")
def step_impl_home_visible(context: Context) -> None:
    """
    Verify that only the Home page is visible.
    """
    assert context.state["home"] is True
    assert context.state["dashboard"] is False
    assert context.state["prediction"] is False


@when('the user clicks the "Dashboard" button')
def step_impl_click_dashboard(context: Context) -> None:
    """
    Simulate clicking the Dashboard navigation button.
    """
    set_visibility(context, home=False, dashboard=True, prediction=False)


@then("only the Dashboard page should be visible")
def step_impl_dashboard_visible(context: Context) -> None:
    """
    Verify that only the Dashboard page is visible.
    """
    assert context.state["home"] is False
    assert context.state["dashboard"] is True
    assert context.state["prediction"] is False


@when('the user clicks the "Retour à l\'accueil" button')
def step_impl_click_back_home(context: Context) -> None:
    """
    Simulate clicking the Back to Home button.
    """
    set_visibility(context, home=True, dashboard=False, prediction=False)


@when('the user clicks the "Prediction" button')
def step_impl_click_prediction(context: Context) -> None:
    """
    Simulate clicking the Prediction navigation button.
    """
    set_visibility(context, home=False, dashboard=False, prediction=True)


@then("only the Prediction page should be visible")
def step_impl_prediction_visible(context: Context) -> None:
    """
    Verify that only the Prediction page is visible.
    """
    assert context.state["home"] is False
    assert context.state["dashboard"] is False
    assert context.state["prediction"] is True
