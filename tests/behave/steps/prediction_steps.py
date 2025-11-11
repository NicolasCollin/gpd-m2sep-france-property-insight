from behave import when, then
from fpi.interface.prediction.prediction_page import run_prediction

# Valid prediction
@when("I run a prediction with valid property data")
def step_run_valid_prediction(context):
    row = context.table[0]
    context.prediction_result = run_prediction(
        postal=row["postal"],
        dept=row["dept"],
        town=row["town"],
        prop_type=row["prop_type"],
        area=float(row["area"]),
        rooms=int(row["rooms"]),
        land=float(row["land"]),
    )

@then('the result should contain "Estimated property price"')
def step_check_valid_prediction(context):
    result = context.prediction_result.lower()
    assert "estimated property price" in result, f"Unexpected result: {context.prediction_result}"

# Invalid prediction
@when("I run a prediction with invalid property data")
def step_run_invalid_prediction(context):
    row = context.table[0]
    context.prediction_result = run_prediction(
        postal=row["postal"],
        dept=row["dept"],
        town=row["town"],
        prop_type=row["prop_type"],
        area=float(row["area"]),
        rooms=int(row["rooms"]),
        land=float(row["land"]),
    )

@then('the result should contain "error" or "failed"')
def step_check_invalid_prediction(context):
    result = context.prediction_result.lower()
    assert "error" in result or "failed" in result, f"Unexpected result: {context.prediction_result}"
