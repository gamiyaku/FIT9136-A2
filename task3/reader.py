import csv
import re
import sys


def print_warning(message: str) -> None:
    """Print a warning message to stderr."""
    print(f"Warning: {message}", file=sys.stderr)


def is_valid_id(value: str) -> bool:
    """Check whether an ID has uppercase letters followed by digits with no leading zero."""
    return re.fullmatch(r"[A-Z]+(0|[1-9][0-9]*)", value) is not None


def is_valid_zone(value: str) -> bool:
    """Check whether a zone only contains uppercase letters."""
    return re.fullmatch(r"[A-Z]+", value) is not None


def is_valid_int(value: str) -> bool:
    """Check whether a string is a valid integer representation."""
    return re.fullmatch(r"-?(0|[1-9][0-9]*)", value) is not None


def is_valid_float(value: str) -> bool:
    """
    Check whether a string is a valid float representation.

    Integers are also accepted as valid float representations.
    Decimal values ending in unnecessary zeros, such as 10.80, are invalid.
    """
    int_pattern = r"-?(0|[1-9][0-9]*)"
    decimal_pattern = r"-?(0|[1-9][0-9]*)\.(0|[0-9]*[1-9])"

    return (
        re.fullmatch(int_pattern, value) is not None
        or re.fullmatch(decimal_pattern, value) is not None
    )


def read_to_table(path: str) -> list[dict[str, str]]:
    """
    Read a CSV file into a table.

    Args:
        path: Path to the CSV file.

    Returns:
        A list of dictionaries. Each dictionary represents one row,
        with headers as keys and all values stored as strings.
    """
    table = []

    with open(path, "r", newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)

        for row in reader:
            record = {}

            for i in range(len(headers)):
                record[headers[i]] = row[i]

            table.append(record)

    return table


def read_robots(robots_path: str) -> list[dict]:
    """
    Read and validate robot data.

    Args:
        robots_path: Path to the robots CSV file.

    Returns:
        A list of valid robot records.
    """
    robots = read_to_table(robots_path)
    valid_robots = []

    for robot in robots:
        valid = (
            is_valid_id(robot["robot_id"])
            and is_valid_int(robot["battery_level"])
            and is_valid_float(robot["max_load"])
            and is_valid_zone(robot["zone"])
        )

        if valid:
            battery_level = int(robot["battery_level"])
            max_load = float(robot["max_load"])
            valid = 0 <= battery_level <= 100 and max_load >= 0

        if valid:
            robot["battery_level"] = int(robot["battery_level"])
            robot["max_load"] = float(robot["max_load"])
            valid_robots.append(robot)
        else:
            print_warning(f"Robot {robot.get('robot_id', '')} has invalid values.")

    return valid_robots


def read_destinations(destinations_path: str) -> list[dict]:
    """
    Read and validate destination data.

    Args:
        destinations_path: Path to the destinations CSV file.

    Returns:
        A list of valid destination records.
    """
    destinations = read_to_table(destinations_path)
    valid_destinations = []

    for destination in destinations:
        valid = (
            is_valid_id(destination["destination_id"])
            and is_valid_zone(destination["zone"])
        )

        if valid:
            valid_destinations.append(destination)
        else:
            print_warning(f"Destination {destination.get('destination_id', '')} has invalid values.")

    return valid_destinations


def read_packages(packages_path: str) -> list[dict]:
    """
    Read and validate package data.

    Args:
        packages_path: Path to the packages CSV file.

    Returns:
        A list of valid package records.
    """
    packages = read_to_table(packages_path)
    valid_packages = []

    for package in packages:
        valid = (
            is_valid_id(package["package_id"])
            and is_valid_float(package["weight"])
        )

        if valid:
            weight = float(package["weight"])
            valid = weight >= 0

        if valid:
            package["weight"] = float(package["weight"])
            valid_packages.append(package)
        else:
            print_warning(f"Package {package.get('package_id', '')} has invalid values.")

    return valid_packages


def read_tasks(
    tasks_path: str,
    destination_ids: list[str],
    package_ids: list[str]
) -> list[dict]:
    """
    Read and validate task data.

    Args:
        tasks_path: Path to the tasks CSV file.
        destination_ids: A list of valid destination IDs.
        package_ids: A list of valid package IDs.

    Returns:
        A list of valid task records.
    """
    tasks = read_to_table(tasks_path)
    valid_tasks = []

    for task in tasks:
        valid = (
            is_valid_id(task["task_id"])
            and is_valid_id(task["source_id"])
            and is_valid_id(task["target_id"])
            and is_valid_id(task["package_id"])
            and task["status"] in ["pending", "complete"]
        )

        if valid and task["source_id"] not in destination_ids:
            valid = False

        if valid and task["target_id"] not in destination_ids:
            valid = False

        if valid and task["package_id"] not in package_ids:
            valid = False

        if valid:
            valid_tasks.append(task)
            
        else:
            print_warning(f"Task {task.get('task_id', '')} has invalid values.")

    return valid_tasks

def read_schedules(
    schedules_path: str,
    robot_ids: list[str],
    task_ids: list[str]
) -> list[dict]:
    """
    Read and validate schedule data.

    Each valid row must contain:
        a schedule ID
        a robot ID
        one or more task IDs

    Args:
        schedules_path: Path to the schedules CSV file.
        robot_ids: A list of valid robot IDs.
        task_ids: A list of valid task IDs.

    Returns:
        A list of valid schedule records.
    """
    schedules = []

    with open(schedules_path, "r", newline="") as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) < 3:
                print_warning("Schedule row has invalid values.")
                continue

            valid = True

            schedule_id = row[0]
            robot_id = row[1]
            schedule_task_ids = row[2:]

            if not is_valid_id(schedule_id):
                valid = False

            if robot_id not in robot_ids:
                valid = False

            for task_id in schedule_task_ids:
                if task_id not in task_ids:
                    valid = False

            if valid:
                schedules.append({
                    "schedule_id": schedule_id,
                    "robot_id": robot_id,
                    "task_ids": schedule_task_ids
                })
            else:
                print_warning(f"Schedule {schedule_id} has invalid values.")

    return schedules


def read_distances(distances_path: str) -> list[list[float]]:
    """
    Read the distance matrix from a CSV file.

    Args:
        distances_path: Path to the distances CSV file.

    Returns:
        A list of lists containing distance values as floats.
    """
    distances = []

    with open(distances_path, "r", newline="") as file:
        reader = csv.reader(file)

        for row in reader:
            distance_row = []

            for value in row:
                distance_row.append(float(value))

            distances.append(distance_row)

    return distances
