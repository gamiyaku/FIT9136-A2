from reader import read_robots, read_destinations, read_packages, read_tasks
from tasker import get_id_list, is_task_executable


def write_feasibility_report(report_path: str, tasks: list[dict], results: list[bool]) -> None:
    """
    Write the task feasibility report to a text file.

    Args:
        report_path: Path to the output report file.
        tasks: A list of task records.
        results: A list of feasibility results aligned with tasks.

    Returns:
        None.
    """
    with open(report_path, "w", newline="") as file:
        file.write("Task Feasibility Report\n\n")
        executable_count = 0
        non_executable_count = 0

        for i in range(len(tasks)):
            if results[i]:
                file.write(f"{tasks[i]['task_id']}: executable\n")
                executable_count += 1
            else:
                file.write(f"{tasks[i]['task_id']}: not executable\n")
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
        robots_path: Path to the robots CSV file.
        destinations_path: Path to the destinations CSV file.
        packages_path: Path to the packages CSV file.
        tasks_path: Path to the tasks CSV file.
        report_path: Path to the output report file.

    Returns:
        None.
    """
    robots = read_robots(robots_path)
    destinations = read_destinations(destinations_path)
    packages = read_packages(packages_path)

    destination_ids = get_id_list(destinations, "destination_id")
    package_ids = get_id_list(packages, "package_id")

    tasks = read_tasks(tasks_path, destination_ids, package_ids)

    results = []

    for task in tasks:
        result = is_task_executable(task, robots, destinations, packages, tasks)
        results.append(result)

    write_feasibility_report(report_path, tasks, results)


if __name__ == "__main__":
    pass
