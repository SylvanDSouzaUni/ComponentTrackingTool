import repositories

#Reusable function to validate integer inputs
def validation_for_integer_input(value, field):
    try:
        integer = int(value)
        stripped_integer = str(integer).strip()
    except Exception:
        raise ValueError(f"{field} must be an integer")
    if integer < 0:
        raise ValueError(f"{field} must be positive")
    if not stripped_integer:
        raise ValueError(f"{field} must not be empty")
    return integer

#Reusable function to validate non-empty inputs
def validation_for_non_empty_input(value, field):
    stripped_value = str(value).strip()
    if not stripped_value:
        raise ValueError(f"'{field}' must not be empty")
    return stripped_value.lower()

#Reusable function to validate string inputs
def validation_for_string_input(value, field):
    stripped_value = str(value).strip().lower()
    if not stripped_value:
        raise ValueError(f"'{field}' must not be empty")
    if stripped_value.isdigit():
        raise ValueError(f"'{field}' must not be an integer")
    return stripped_value

#Reusable function to validate the actor of actions
def validate_actor(actor):
    validation_for_string_input(actor, "ACTOR")
    if repositories.return_user(actor) is None:
        raise ValueError(f"Actor '{actor}' does not exist.")
