from behave import given, then, when


@given("we have behave installed")
def step_installation(context):
    pass


@when("we implement a test")
def step_implement(context):
    assert True is not False


@then("behave will test it for us!")
def step_test(context):
    assert context.failed is False
