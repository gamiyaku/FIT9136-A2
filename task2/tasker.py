def find_record_by_id(table: list[dict], id_field: str, record_id: str) -> dict | None:
    """
    Return the first record in a table whose ID matches the given record ID.
    """
    for record in table:
        if record[id_field] == record_id:
            return record

    return None


def get_id_list(table: list[dict], id_field: str) -> list[str]:
    """
    Extract all ID values from a table.
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
    Return a list of executability results aligned with the tasks table.
    """
    results = []

    for task in tasks:
        result = is_task_executable(task, robots, destinations, packages, tasks)
        results.append(result)

    return results
