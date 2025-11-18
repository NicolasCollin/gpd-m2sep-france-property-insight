from unittest.mock import MagicMock, patch

from behave import then, when

from fpi.interface.prediction.prediction_page import run_prediction


# --- Helper to mock requests.post ---
def mock_post_success(*args, **kwargs):
    """Mock a successful prediction response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"predicted_price": 123456}
    return mock_response


def mock_post_failure(*args, **kwargs):
    """Mock a failed prediction response (simulate server error)."""
    raise Exception("Prediction failed: simulated server error")


# --- Valid prediction ---
@when("I run a prediction with valid property data")
def step_run_valid_prediction(context):
    row = context.table[0]
    with patch("fpi.interface.prediction.prediction_page.requests.post", side_effect=mock_post_success):
        context.prediction_result = run_prediction(
            postal=row["postal"],
            prop_type=row["prop_type"],
            area=float(row["area"]),
            rooms=int(row["rooms"]),
            land=float(row["land"]),
        )


@then('the result should contain "Estimated property price"')
def step_check_valid_prediction(context):
    result = context.prediction_result.lower()
    assert "estimated property price" in result, f"Unexpected result: {context.prediction_result}"


# --- Invalid prediction ---
@when("I run a prediction with invalid property data")
def step_run_invalid_prediction(context):
    row = context.table[0]
    with patch("fpi.interface.prediction.prediction_page.requests.post", side_effect=mock_post_failure):
        context.prediction_result = run_prediction(
            postal=row["postal"],
            prop_type=row["prop_type"],
            area=float(row["area"]),
            rooms=int(row["rooms"]),
            land=float(row["land"]),
        )


@then('the result should contain "error" or "failed"')
def step_check_invalid_prediction(context):
    result = context.prediction_result.lower()
    assert "error" in result or "failed" in result, f"Unexpected result: {context.prediction_result}"
