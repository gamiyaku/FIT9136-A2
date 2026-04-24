import sys
import csv

def read_robots(robots_path: str) -> list[list]:
    """
    Read robot data from a CSV file.

    Args:
        robots_path: Path to the robots CSV file.

    Returns:
        A list containing four aligned lists:
        - robot_ids (list[str])
        - battery_levels (list[int])
        - max_loads (list[float])
        - robot_zones (list[str])
    """
    robot_ids = []
    battery_levels = []
    max_loads = []
    robot_zones = []

    with open(robots_path, "r", newline="") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            robot_id = row[0]
            battery_level = int(row[1])
            max_load = float(row[2])
            zone = row[3]

            valid = True

            if battery_level < 0 or battery_level > 100:
                print_warning(f"Robot {robot_id} has invalid battery level ({battery_level}).")
                valid = False

            if max_load < 0:
                print_warning(f"Robot {robot_id} has invalid max load ({max_load}).")
                valid = False

            if not is_valid_zone(zone):
                print_warning(f"Robot {robot_id} has invalid zone ({zone}).")
                valid = False

            if valid:
                robot_ids.append(robot_id)
                battery_levels.append(battery_level)
                max_loads.append(max_load)
                robot_zones.append(zone)

    return [robot_ids, battery_levels, max_loads, robot_zones]


def read_destinations(destinations_path: str) -> list[list]:
    """
    Read destination data from a CSV file.

    Args:
        destinations_path: Path to the destinations CSV file.

    Returns:
        A list containing two aligned lists:
        - destination_ids (list[str])
        - destination_zones (list[str])
    """
    destination_ids = []
    destination_zones = []

    with open(destinations_path, "r", newline="") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            destination_id = row[0]
            zone = row[1]

            if not is_valid_zone(zone):
                print_warning(f"Destination {destination_id} has invalid zone ({zone}).")
                continue

            destination_ids.append(destination_id)
            destination_zones.append(zone)

    return [destination_ids, destination_zones]


def read_packages(packages_path: str) -> list[list]:
    """
    Read package data from a CSV file.

    Args:
        packages_path: Path to the packages CSV file.

    Returns:
        A list containing two aligned lists:
        - package_ids (list[str])
        - package_weights (list[float])
    """
    package_ids = []
    package_weights = []

    with open(packages_path, "r", newline="") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            package_id = row[0]
            weight = float(row[1])

            if weight < 0:
                print_warning(f"Package {package_id} has invalid weight ({weight}).")
                continue

            package_ids.append(package_id)
            package_weights.append(weight)

    return [package_ids, package_weights]


def read_tasks(
    tasks_path: str,
    destination_ids: list[str],
    package_ids: list[str]
) -> list[list]:
    """
    Read task data from a CSV file.

    Args:
        tasks_path: Path to the tasks CSV file.
        destination_ids: List of valid destination IDs.
        package_ids: List of valid package IDs.

    Returns:
        A list containing five aligned lists:
        - task_ids (list[str])
        - source_ids (list[str])
        - target_ids (list[str])
        - task_package_ids (list[str])
        - statuses (list[str])
    """
    task_ids = []
    source_ids = []
    target_ids = []
    task_package_ids = []
    statuses = []

    with open(tasks_path, "r", newline="") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            task_id = row[0]
            source_id = row[1]
            target_id = row[2]
            package_id = row[3]
            status = row[4]

            valid = True

            if source_id not in destination_ids:
                print_warning(f"Task {task_id} has invalid source_id ({source_id}).")
                valid = False

            if target_id not in destination_ids:
                print_warning(f"Task {task_id} has invalid target_id ({target_id}).")
                valid = False

            if package_id not in package_ids:
                print_warning(f"Task {task_id} has invalid package_id ({package_id}).")
                valid = False

            if status not in ["pending", "complete"]:
                print_warning(f"Task {task_id} has invalid status ({status}).")
                valid = False

            if valid:
                task_ids.append(task_id)
                source_ids.append(source_id)
                target_ids.append(target_id)
                task_package_ids.append(package_id)
                statuses.append(status)

    return [task_ids, source_ids, target_ids, task_package_ids, statuses]

def is_valid_zone(zone: str) -> bool:
    """
    Check whether a zone value is valid.

    Args:
        zone: The zone string to validate.

    Returns:
        True if the zone is non-empty, contains only letters,
        and is all uppercase. False otherwise.
    """
    return zone != "" and zone.isalpha() and zone.isupper()


def print_warning(message: str) -> None:
    """
    Print a warning message to the standard error buffer.

    Args:
        message: The warning message to print.

    Returns:
        None.
    """
    print(f"Warning: {message}", file=sys.stderr)

def is_task_executable(
    task_id: str,
    package_ids: list[str],
    package_weights: list[float],
    robot_ids: list[str],
    max_loads: list[float],
    robot_zones: list[str],
    destination_ids: list[str],
    destination_zones: list[str],
    task_ids: list[str],
    source_ids: list[str],
    target_ids: list[str],
    task_package_ids: list[str]
) -> bool:
    """
    Check whether a task is executable.

    Args:
        task_id: The ID of the task to check.
        package_ids: A list of package IDs.
        package_weights: A list of package weights aligned with package_ids.
        robot_ids: A list of robot IDs.
        max_loads: A list of maximum loads aligned with robot_ids.
        robot_zones: A list of robot zones aligned with robot_ids.
        destination_ids: A list of destination IDs.
        destination_zones: A list of destination zones aligned with destination_ids.
        task_ids: A list of task IDs.
        source_ids: A list of source destination IDs aligned with task_ids.
        target_ids: A list of target destination IDs aligned with task_ids.
        task_package_ids: A list of package IDs aligned with task_ids.

    Returns:
        True if the task is executable. False otherwise.
    """
    task_index = task_ids.index(task_id)

    source_id = source_ids[task_index]
    target_id = target_ids[task_index]
    package_id = task_package_ids[task_index]

    package_index = package_ids.index(package_id)
    package_weight = package_weights[package_index]

    source_index = destination_ids.index(source_id)
    source_zone = destination_zones[source_index]

    target_index = destination_ids.index(target_id)
    target_zone = destination_zones[target_index]

    for i in range(len(robot_ids)):
        same_source_zone = robot_zones[i] == source_zone
        same_target_zone = robot_zones[i] == target_zone
        enough_capacity = max_loads[i] >= package_weight

        if same_source_zone and same_target_zone and enough_capacity:
            return True

    return False


def write_feasibility_report(report_path: str, task_ids: list[str], results: list[bool]) -> None:
    """
    Write the task feasibility report to a text file.

    Args:
        report_path: The path to the output report file.
        task_ids: A list of task IDs.
        results: A list of feasibility results aligned with task_ids.

    Returns:
        None.
    """
    with open(report_path, "w", newline="") as file:
        executable_count = 0
        non_executable_count = 0

        for i in range(len(task_ids)):
            if results[i]:
                file.write(f"{task_ids[i]}: executable\n")
                executable_count += 1
            else:
                file.write(f"{task_ids[i]}: not executable\n")
                non_executable_count += 1

        file.write("\n")
        file.write(f"Executable tasks: {executable_count}\n")
        file.write(f"Non-executable tasks: {non_executable_count}")


def main(
    robots_path: str,
    destinations_path: str,
    packages_path: str,
    tasks_path: str,
    report_path: str
) -> None:
    """
    Run the full task feasibility workflow.

    Args:
        robots_path: The path to the robots CSV file.
        destinations_path: The path to the destinations CSV file.
        packages_path: The path to the packages CSV file.
        tasks_path: The path to the tasks CSV file.
        report_path: The path to the output report file.

    Returns:
        None.
    """
    robot_ids, battery_levels, max_loads, robot_zones = read_robots(robots_path)
    destination_ids, destination_zones = read_destinations(destinations_path)
    package_ids, package_weights = read_packages(packages_path)
    task_ids, source_ids, target_ids, task_package_ids, statuses = read_tasks(
        tasks_path, destination_ids, package_ids
    )

    results = []

    for task_id in task_ids:
        result = is_task_executable(
            task_id,
            package_ids,
            package_weights,
            robot_ids,
            max_loads,
            robot_zones,
            destination_ids,
            destination_zones,
            task_ids,
            source_ids,
            target_ids,
            task_package_ids
        )
        results.append(result)

    write_feasibility_report(report_path, task_ids, results)


if __name__ == "__main__":
    pass

