# Task Registration and Prediction REST API
The goal of this REST API is to register tasks and use the data to make predictions. A task can be any piece of code with a given set of input that runs on a given resource. Therefore, a workflow can be made of multiple tasks. The idea is to give the user flexibility to use the REST API as needed for whatever tasks are defined. Also, users would be able to call it to register specific tasks whereas PW could register the entire job as a task.

To run the tests:
1. Start the REST API: `python application.py`
2. Run the tests: `python test.py`

See `run_dummy_task.py` for a usage example.

Once the REST API is fully developed users should be able to register any task by:
1. Providing the task inputs (any key-value dictionary)
2. Pointing to the resource name, partition and whether it uses lustre or not. The PW API will be used to retrieve any further information from the resource.


