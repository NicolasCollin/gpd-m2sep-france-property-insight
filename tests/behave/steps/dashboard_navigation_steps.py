from behave import then, when

# Simulated dashboard state
DASHBOARD_STATE = {"tabs": ["Overview", "Data visualization"], "active_tab": None}


@when('the user opens the "{tab_name}" tab')
def step_open_tab(context, tab_name):
    if tab_name not in DASHBOARD_STATE["tabs"]:
        raise ValueError(f"Tab '{tab_name}' does not exist")
    DASHBOARD_STATE["active_tab"] = tab_name


@then('the "{tab_name}" tab should be visible')
def step_check_tab_visible(context, tab_name):
    assert DASHBOARD_STATE["active_tab"] == tab_name, f"Expected active tab '{tab_name}', but got '{DASHBOARD_STATE['active_tab']}'"
