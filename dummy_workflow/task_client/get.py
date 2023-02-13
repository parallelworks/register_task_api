import requests
TASKS_URL: str = "http://127.0.0.1:5000/tasks"

def get_tasks_by_name(name: str) -> list:
    tasks = requests.get(TASKS_URL).json()
    tasks_with_name = []
    for task in tasks['tasks']:
        if task['name'] == name:
            tasks_with_name.append(task)
    
    return tasks_with_name


if __name__ == '__main__':
    tasks_with_name = get_tasks_by_name('avidalto-sleep_geometric_mean')
    print(tasks_with_name)