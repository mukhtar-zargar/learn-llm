import json
import os
from semantic_kernel.functions import kernel_function


class CareerTrackerPlugin:
    @kernel_function(description="Get a list of the jobs worked during the user's career")
    def get_career_history(self) -> str:
        print("Reading career history from file...")
        print(os.path.exists("data/jobs.txt"))  # or adjust the path
        with open("data/jobs.txt", "r") as file:
            raw_data = file.read()
            print("Reading career history from file...", raw_data)

        return raw_data
        