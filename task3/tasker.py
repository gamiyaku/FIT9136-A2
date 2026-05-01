def find_record_by_id(table: list[dict], id_field: str, record_id: str) -> dict | None:
    """
    Find a record in a table by matching a given ID value.

    Args:
        table: A table represented as a list of dictionaries.
        id_field: The dictionary key that stores the ID value.
        record_id: The ID value to search for.

    Returns:
        The first matching record if one is found, otherwise None.
    """
    for record in table:
        if record[id_field] == record_id:
            return record

    return None


def get_id_list(table: list[dict], id_field: str) -> list[str]:
    """
    Extract all ID values from a table.

    Args:
        table: A table represented as a list of dictionaries.
        id_field: The dictionary key that stores the ID value.

    Returns:
        A list containing the ID values from the given field for all records in the table.
    """
    ids = []

    for record in table:
        ids.append(record[id_field])

    return ids


def is_task_executable(
    task: dict,
    robots: list[dict],
    destinations: list[dict],
    packages: list[dict],
    tasks: list[dict]
) -> bool:
    """
    Check whether a single task is executable.

    A task is executable if there exists at least one robot that:
        is in the same zone as the source destination,
        is in the same zone as the target destination,
        has enough load capacity for the package.
    
     Args:
        task: The task record to check.
        robots: A list of robot records.
        destinations: A list of destination records.
        packages: A list of package records.
        tasks: A list of all task records, included for interface consistency.
    
    Returns:
        True if the task is executable, otherwise False.
    """
    source = find_record_by_id(destinations, "destination_id", task["source_id"])
    target = find_record_by_id(destinations, "destination_id", task["target_id"])
    package = find_record_by_id(packages, "package_id", task["package_id"])

    if source is None or target is None or package is None:
        return False

    source_zone = source["zone"]
    target_zone = target["zone"]
    package_weight = float(package["weight"])

    for robot in robots:
        same_source_zone = robot["zone"] == source_zone
        same_target_zone = robot["zone"] == target_zone
        enough_capacity = float(robot["max_load"]) >= package_weight

        if same_source_zone and same_target_zone and enough_capacity:
            return True

    return False


def get_task_results(
    tasks: list[dict],
    robots: list[dict],
    destinations: list[dict],
    packages: list[dict]
) -> list[bool]:
    """
    Compute executability for all tasks.

    Args:
        tasks: A list of task records.
        robots: A list of robot records.
        destinations: A list of destination records.
        packages: A list of package records.
    
    Returns:
        A list of boolean results aligned with the tasks table.
        Each value is True if the corresponding task is executable,
        otherwise False.
    """
    results = []

    for task in tasks:
        result = is_task_executable(task, robots, destinations, packages, tasks)
        results.append(result)

    return results

def check_schedule(
    schedule: dict,
    distances: list[list[float]],
    robots: list[dict],
    destinations: list[dict],
    packages: list[dict],
    tasks: list[dict]
) -> list[tuple] | None:
    """
    Check whether a schedule is feasible.
    The robot starts at the origin, completes each task in the given order, and returns to the origin after all tasks are complete.
    
    Args:
        schedule: A schedule record containing schedule_id, robot_id, and a list of task_ids.
        distances: A distance matrix where index 0 is the origin and destination i corresponds to row/column i + 1.
        robots: A list of robot records.
        destinations: A list of destination records.
        packages: A list of package records.
        tasks: A list of task records.

    Returns:
        A list of tuples describing the robot state over time if the schedule is feasible. Each tuple contains:
            time elapsed in hours,
            total distance travelled in km,
            distance from the origin in km,
            remaining battery percentage.
        Returns None if the schedule is infeasible.
    """
    from math import inf

    robot = find_record_by_id(robots, "robot_id", schedule["robot_id"])
    if robot is None:
        return None

    battery = float(robot["battery_level"])
    zone = robot["zone"]
    max_load = float(robot["max_load"])

    current_location = 0  # origin index
    total_distance = 0
    time_elapsed = 0

    results = [(0, 0, 0, battery)]

    for task_id in schedule["task_ids"]:
        task = find_record_by_id(tasks, "task_id", task_id)
        if task is None:
            return None
        
        source = find_record_by_id(destinations, "destination_id", task["source_id"])
        target = find_record_by_id(destinations, "destination_id", task["target_id"])
        package = find_record_by_id(packages, "package_id", task["package_id"])

        if source is None or target is None or package is None:
            return None
        
        if source["zone"] != zone or target["zone"] != zone:
            return None

        weight = float(package["weight"])

        if weight > max_load:
            return None
        
        source_index = destinations.index(source) + 1
        target_index = destinations.index(target) + 1

        d1 = distances[current_location][source_index]

        battery -= d1 * 1 
        if battery <= 0:
            return None

        total_distance += d1
        time_elapsed += d1 / 15
        current_location = source_index

        results.append((
    time_elapsed,
    total_distance,
    distances[current_location][0],
    battery
))
        
        d2 = distances[source_index][target_index]

        battery -= d2 * (1 + 0.5 * weight)
        if battery <= 0:
            return None

        total_distance += d2
        time_elapsed += d2 / 15
        current_location = target_index

        results.append((
    time_elapsed,
    total_distance,
    distances[current_location][0],
    battery
))

        d3 = distances[current_location][0]

    battery -= d3 * 1
    if battery < 0:
        return None

    total_distance += d3
    time_elapsed += d3 / 15

    results.append((time_elapsed, total_distance, 0, battery))

    return results
