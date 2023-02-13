import task_client

all_tasks = task_client.get.get_tasks_by_name('avidalto-sleep_geometric_mean')
print(all_tasks)