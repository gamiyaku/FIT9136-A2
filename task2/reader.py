import csv
import os
import re
import sys


def print_warning(message: str) -> None:
    """
    Print a warning message to stderr.
    """
    print(f"Warning: {message}", file=sys.stderr)


def is_valid_id(value: str) -> bool:
    """
    A valid ID:
    - starts with one or more uppercase letters
    - followed by an integer with no leading zeros, except 0 itself

    Examples:
    A3213 -> valid
    AB0456 -> invalid
    """
    return re.fullmatch(r"[A-Z]+(0|[1-9][0-9]*)", value) is not None


def is_valid_zone(zone: str) -> bool:
    """
    A valid zone is one or more uppercase letters.
    """
    return re.fullmatch(r"[A-Z]+", zone) is not None


def is_valid_int(value: str) -> bool:
    """
    A valid integer may:
    - optionally start with '-'
    - then contain digits
    - not use leading zeros except for 0 itself

    Examples:
    0, 12, -3 are valid
    03, -09 are invalid
    """
    return re.fullmatch(r"-?(0|[1-9][0-9]*)", value) is not None


def is_valid_float(value: str) -> bool:
    """
    A valid float may:
    - optionally start with '-'
    - contain a valid integer part
    - optionally contain a decimal part with at least one digit after '.'

    Examples:
    1, -2, 3.5, -0.75 are valid
    .5, 01.2, 2. are invalid
    """
    return re.fullmatch(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?", value) is not None


def validate_value(value: str, value_type: str) -> bool:
    """
    Validate a raw CSV value against the expected type.
    """
    if value_type == "id":
        return is_valid_id(value)
    if value_type == "zone":
        return is_valid_zone(value)
    if value_type == "int":
        return is_valid_int(value)
    if value_type == "float":
        return is_valid_float(value)
    if value_type == "status":
        return value in ["pending", "complete"]
    return False


def convert_value(value: str, value_type: str):
    """
    Convert a validated CSV string into the correct Python type.
    """
    if value_type == "int":
        return int(value)
    if value_type == "float":
        return float(value)
    return value


def get_schema(csv_path: str) -> list[tuple[str, str]]:
    """
    Return the expected schema for the given CSV file.
    """
    file_name = os.path.basename(csv_path)

    if file_name == "robots.csv":
        return [
            ("robot_id", "id"),
            ("battery_level", "int"),
            ("max_load", "float"),
            ("zone", "zone"),
        ]
    if file_name == "destinations.csv":
        return [
            ("destination_id", "id"),
            ("zone", "zone"),
        ]
    if file_name == "packages.csv":
        return [
            ("package_id", "id"),
            ("weight", "float"),
        ]
    if file_name == "tasks.csv":
        return [
            ("task_id", "id"),
            ("source_id", "id"),
            ("target_id", "id"),
            ("package_id", "id"),
            ("status", "status"),
        ]

    raise ValueError(f"Unsupported CSV file: {csv_path}")


def validate_row(
    row: list[str],
    schema: list[tuple[str, str]],
    row_number: int,
    csv_path: str
) -> bool:
    """
    Validate one row from a CSV file against its schema.
    """
    if len(row) != len(schema):
        print_warning(
            f"{os.path.basename(csv_path)} row {row_number} has an invalid number of columns."
        )
        return False

    for i in range(len(schema)):
        field_name, value_type = schema[i]
        raw_value = row[i].strip()

        if not validate_value(raw_value, value_type):
            print_warning(
                f"{os.path.basename(csv_path)} row {row_number} has invalid {field_name} ({raw_value})."
            )
            return False

    return True


def apply_bounds_check(record: dict, csv_path: str) -> bool:
    """
    Apply non-regex validation rules after type conversion.
    """
    file_name = os.path.basename(csv_path)

    if file_name == "robots.csv":
        if record["battery_level"] < 0 or record["battery_level"] > 100:
            print_warning(
                f"Robot {record['robot_id']} has invalid battery level ({record['battery_level']})."
            )
            return False

        if record["max_load"] < 0:
            print_warning(
                f"Robot {record['robot_id']} has invalid max load ({record['max_load']})."
            )
            return False

    elif file_name == "packages.csv":
        if record["weight"] < 0:
            print_warning(
                f"Package {record['package_id']} has invalid weight ({record['weight']})."
            )
            return False

    return True


def read_to_table(csv_path: str) -> list[dict]:
    """
    Read a CSV file and return a table represented as a list of dictionaries.

    Invalid rows are skipped.
    """
    schema = get_schema(csv_path)
    table = []

    with open(csv_path, "r", newline="") as file:
        reader = csv.reader(file)
        next(reader, None)

        for row_number, row in enumerate(reader, start=2):
            if not validate_row(row, schema, row_number, csv_path):
                continue

            record = {}

            for i in range(len(schema)):
                field_name, value_type = schema[i]
                raw_value = row[i].strip()
                record[field_name] = convert_value(raw_value, value_type)

            if apply_bounds_check(record, csv_path):
                table.append(record)

    return table


def read_robots(robots_path: str) -> list[dict]:
    """
    Read robot data as a table.
    """
    return read_to_table(robots_path)


def read_destinations(destinations_path: str) -> list[dict]:
    """
    Read destination data as a table.
    """
    return read_to_table(destinations_path)


def read_packages(packages_path: str) -> list[dict]:
    """
    Read package data as a table.
    """
    return read_to_table(packages_path)


def read_tasks(
    tasks_path: str,
    destination_ids: list[str],
    package_ids: list[str]
) -> list[dict]:
    """
    Read task data as a table and validate destination/package references.
    """
    tasks = read_to_table(tasks_path)
    valid_tasks = []

    for task in tasks:
        valid = True

        if task["source_id"] not in destination_ids:
            print_warning(f"Task {task['task_id']} has invalid source_id ({task['source_id']}).")
            valid = False

        if task["target_id"] not in destination_ids:
            print_warning(f"Task {task['task_id']} has invalid target_id ({task['target_id']}).")
            valid = False

        if task["package_id"] not in package_ids:
            print_warning(f"Task {task['task_id']} has invalid package_id ({task['package_id']}).")
            valid = False

        if valid:
            valid_tasks.append(task)

    return valid_tasks