from reader import (
    read_robots,
    read_destinations,
    read_packages,
    read_tasks,
    read_schedules,
    read_distances
)

from tasker import get_id_list, is_task_executable, check_schedule

import pandas as pd
import matplotlib.pyplot as plt


def write_feasibility_report(
    report_path: str,
    tasks: list[dict],
    results: list[bool],
    schedules: list[dict],
    schedule_report: list
) -> None:
    """
    Write the task and schedule feasibility report to a text file.

    Args:
        report_path: Path to the output report file.
        tasks: A list of task records.
        results: A list of task feasibility results aligned with tasks.
        schedules: A list of schedule records.
        schedule_report: A list containing the result of check_schedule for each schedule.
    
    Return:
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
        file.write(f"Non-executable tasks: {non_executable_count}\n\n")

        file.write("Schedule feasibility\n\n")

        for i in range(len(schedules)):
            schedule = schedules[i]
            result = schedule_report[i]

            if result is None:
                file.write(f"{schedule['schedule_id']}: Infeasible\n")
            else:
                final_state = result[-1]
                final_time = final_state[0]
                final_distance = final_state[1]
                final_battery = final_state[3]

                file.write(
                    f"{schedule['schedule_id']}: Robot {schedule['robot_id']} "
                    f"completed schedule in {final_time:.2f} hours and covered "
                    f"{final_distance:.2f} km. Battery remaining {final_battery:.2f}%.\n"
                )


def plot_schedule_positions(
    schedules: list[dict],
    schedule_report: list,
    plot_file: str
) -> None:
    """
    Plot each feasible schedule's robot distance from the origin over time.

    Only feasible schedules are plotted. Each line represents one schedule.

    Args:
        schedules: A list of schedule records.
        schedule_report: A list containing the result of check_schedule for each schedule. Each element is either None or a list of robot state tuples.
        plot_file: Path to the output plot image file.

    Returns:
        None.
    """
    plt.figure()

    for i in range(len(schedules)):
        result = schedule_report[i]

        if result is not None:
            robot_id = schedules[i]["robot_id"]

            df = pd.DataFrame(
                result,
                columns=[
                    "time",
                    "total_distance",
                    "distance_from_origin",
                    "battery"
                ]
            )

            plt.plot(
                df["time"],
                df["distance_from_origin"],
                marker="o",
                label=robot_id
            )

    plt.title("Robot Position Over Time")
    plt.xlabel("Time (hours)")
    plt.ylabel("Distance from Origin (km)")
    plt.legend()
    plt.grid(True)
    plt.savefig(plot_file)
    plt.close()


def main(
    robots_path: str,
    destinations_path: str,
    packages_path: str,
    tasks_path: str,
    schedules_path: str,
    distances_path: str,
    report_path: str,
    plot_file: str
) -> None:
    """
    Run the full task and schedule feasibility workflow.

    With functions:
        reads and validates all input files,
        checks whether each task is executable,
        checks whether each schedule is feasible,
        writes the feasibility report,
        generates the schedule position plot.
    
    Args:
        robots_path: Path to the robots CSV file.
        destinations_path: Path to the destinations CSV file.
        packages_path: Path to the packages CSV file.
        tasks_path: Path to the tasks CSV file.
        schedules_path: Path to the schedules CSV file.
        distances_path: Path to the distances CSV file.
        report_path: Path to the output report file.
        plot_file: Path to the output plot image file.

    Returns:
        None.
    """
    robots = read_robots(robots_path)
    destinations = read_destinations(destinations_path)
    packages = read_packages(packages_path)

    destination_ids = get_id_list(destinations, "destination_id")
    package_ids = get_id_list(packages, "package_id")
    robot_ids = get_id_list(robots, "robot_id")

    tasks = read_tasks(tasks_path, destination_ids, package_ids)
    task_ids = get_id_list(tasks, "task_id")

    schedules = read_schedules(schedules_path, robot_ids, task_ids)
    distances = read_distances(distances_path)

    results = []

    for task in tasks:
        result = is_task_executable(task, robots, destinations, packages, tasks)
        results.append(result)

    schedule_report = []

    for schedule in schedules:
        result = check_schedule(
            schedule,
            distances,
            robots,
            destinations,
            packages,
            tasks
        )
        schedule_report.append(result)

    write_feasibility_report(
        report_path,
        tasks,
        results,
        schedules,
        schedule_report
    )

    plot_schedule_positions(
        schedules,
        schedule_report,
        plot_file
    )


if __name__ == "__main__":
    main(
        "robots.csv",
        "destinations.csv",
        "packages.csv",
        "tasks.csv",
        "schedules.csv",
        "distances.csv",
        "report.txt",
        "schedule_positions.png"
    )
