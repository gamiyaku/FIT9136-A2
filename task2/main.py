from reader import read_robots, read_destinations, read_packages, read_tasks
from tasker import get_id_list, get_task_results


def write_feasibility_report(report_path: str, tasks: list[dict], results: list[bool]) -> None:
    """
    Write the task feasibility report to a text file.
    """
    with open(report_path, "w", newline="") as file:
        executable_count = 0
        non_executable_count = 0

        for i in range(len(tasks)):
            task = tasks[i]

            if results[i]:
                file.write(f"{task['task_id']}: executable\n")
                executable_count += 1
            else:
                file.write(f"{task['task_id']}: not executable\n")
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
    """
    robots = read_robots(robots_path)
    destinations = read_destinations(destinations_path)
    packages = read_packages(packages_path)

    destination_ids = get_id_list(destinations, "destination_id")
    package_ids = get_id_list(packages, "package_id")

    tasks = read_tasks(tasks_path, destination_ids, package_ids)
    results = get_task_results(tasks, robots, destinations, packages)

    write_feasibility_report(report_path, tasks, results)


if __name__ == "__main__":
    pass