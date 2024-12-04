import ast
import os
import json
import time

import subprocess
from anthropic import Anthropic

from selenium.webdriver.common.keys import Keys
from helium import start_chrome, write, S, kill_browser
from datetime import datetime
import shutil
import webbrowser

from html_builder import generate_html


def sleep(no_of_seconds):
    print(f"waiting for {no_of_seconds} seconds for next step")
    for remaining in range(no_of_seconds, 0, -1):
      print(f"{remaining} seconds remaining", end="\r")  # Overwrites the same line
      time.sleep(1)

class ChatHandler:
    @staticmethod
    def send_message(message):
        """
        Sends a message through the chat interface using helium.

        Args:
            message (str): The message to be sent.
            delay (int): Delay before sending the message, in seconds.
        """
        textarea = S('[placeholder="Type a message to send to Claude to control the computer..."]')  # Replace with the appropriate selector
        write(message, into=textarea)
        textarea.web_element.send_keys(Keys.RETURN)  # Use Keys.ENTER if needed
        print(f"********************************")
        print(f"running step: {message}")
        sleep(5)

        t = 0
        while textarea.web_element.value_of_css_property('display') == 'none':
            print(f"textarea is disabled since {t} seconds, waiting for it to be enabled again", end="\r")
            time.sleep(1)
            t += 1

        print(f"textarea has been disabled since {t} seconds and is enabled again now, moving to next step")


class FileHandler:
    @staticmethod
    def read_json(file_path):
        """
        Reads and parses a JSON file.

        Args:
            file_path (str): Path to the JSON file.

        Returns:
            dict: Parsed JSON data.
        """
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def write_to_file(file_path, data):
        """
        Writes data to a file.

        Args:
            file_path (str): Path to the output file.
            data (str): Data to write to the file.
        """
        with open(file_path, 'a') as file:
            file.write(str(data))
            file.write("\n")

    @staticmethod
    def read_text(file_path):
        """
        Reads text data from a file.

        Args:
            file_path (str): Path to the text file.

        Returns:
            str: Content of the file.
        """
        with open(file_path, 'r') as file:
            return file.read()


class DockerHandler:
    @staticmethod
    def copy_folder_from_container(container_name, source_file, destination_file):
        """
        Copies a folder from a Docker container to the host system.

        Args:
            container_name (str): Name of the Docker container.
            source_file (str): Path of the folder inside the container.
            destination_file (str): Destination path on the host system.
        """
        try:
            command = ["docker", "cp", f"{container_name}:{source_file}", destination_file]
            subprocess.run(command, check=True)
        except Exception as e:
            print(f"Unexpected error: {e}")

    @staticmethod
    def delete_file_from_container(container_name, file_path):
        """
        Deletes a file from a Docker container.

        Args:
            container_name (str): Name of the Docker container.
            file_path (str): Path of the file inside the container to be deleted.
        """
        try:
            # Construct the command to delete the file inside the container
            command = ["docker", "exec", container_name, "rm", "-f", file_path]
            subprocess.run(command, check=True)
            print(f"File '{file_path}' deleted from container '{container_name}'.")
        except subprocess.CalledProcessError as e:
            print(f"Error during deleting file: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    @staticmethod
    def delete_folder_from_container(container_name, folder_path):
        """
        Deletes a folder from a Docker container.

        Args:
            container_name (str): Name of the Docker container.
            folder_path (str): Path of the folder inside the container to be deleted.
        """
        try:
            # Construct the command to delete the folder inside the container
            command = ["docker", "exec", container_name, "rm", "-rf", folder_path]
            subprocess.run(command, check=True)
            print(f"Folder '{folder_path}' deleted from container '{container_name}'.")
        except subprocess.CalledProcessError as e:
            print(f"Error during folder deletion: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


class ScenarioValidator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key)

    def validate_scenario(self, bot_data, scenario_data):
        """
        Validates the test scenario based on bot output and test scenario details.

        Args:
            bot_data (str): Bot data for the scenario.
            scenario_data (str): Path to the test scenario JSON file.

        Returns:
            dict: Validation result in the format {'scenario_tested_successfully': True/False}.
        """

        messages = [{
            "role": "user",
            "content": f"""
            You are an expert at telling if the test scenario has been validated successfully or not.
            You are provided with the Test scenario details like description and steps to perform a test scenario.
            A bot has performed the task and provided with you step-by-step details as briefly as possible.
            Based on the bot-provided information you need to respond if the scenario was successfully validated or not.

            Test Scenario Information:
             {scenario_data}
            Bot Information:
            {bot_data}

            Sample Output Format:
            {{'scenario_tested_successfully': True}}
            {{'scenario_tested_successfully': False}}
            """
        }]
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=messages,
            max_tokens=8192
        )
        output = response.content[0].text
        start_index = output.find('{')
        right_bracket = output.rfind('}')
        parsed_response = output[start_index:right_bracket + 1]
        return ast.literal_eval(parsed_response)


class TestScenarioExecutor:
    def __init__(self, api_key):
        self.validator = ScenarioValidator(api_key)

    @staticmethod
    def move_png_files(source_folder, destination_folder):
        """
        Moves all .png files from source_folder to destination_folder.

        Args:
            source_folder (str): Path to the folder containing the files.
            destination_folder (str): Path to the folder where .png files should be moved.
        """
        try:
            # Ensure the destination folder exists
            os.makedirs(destination_folder, exist_ok=True)

            # Iterate through the files in the source folder
            for file_name in os.listdir(source_folder):
                if file_name.endswith('.png'):  # Check if the file is a .png file
                    source_path = os.path.join(source_folder, file_name)
                    destination_path = os.path.join(destination_folder, file_name)

                    # Move the file
                    shutil.move(source_path, destination_path)
        except Exception as e:
            print(f"An error occurred: {e}")

    @staticmethod
    def delete_folder(folder_path):
        """
        Deletes a folder using subprocess.

        Args:
            folder_path (str): Path to the folder to be deleted.
        """
        try:
            # Construct the command to delete the folder
            command = ["rm", "-rf", folder_path]
            # Run the command
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during folder deletion: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


    def execute_scenario(self, scenario_json_data, timestamp):
        """
        Executes a test scenario and validates it.

        Args:
            scenario_json_data (dict): Path to the test scenario JSON file.
            timestamp (str): timestamp str

        Returns:
            dict: Validation result.
        """
        # Run the scenario test steps
        scenario_id = scenario_json_data['scenario_id']
        print("\n\n")
        print(f"{scenario_id}: Started")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for i, step in enumerate(scenario_json_data['steps']):
            ChatHandler.send_message(step)
        # Handle Docker output
        container_name = "qodex-ai-frontend-agent"
        docker_source_file_folder = "/tmp/outputs"
        DockerHandler.copy_folder_from_container(container_name, docker_source_file_folder, script_dir)

        text_file_path = os.path.join(script_dir, "/outputs/request_response.txt".lstrip("/"))
        bot_data = FileHandler.read_text(text_file_path)
        validation_result = self.validator.validate_scenario(
            bot_data=bot_data,
            scenario_data=str(scenario_json_data)
        )

        # Log results
        destination_folder = os.path.join(script_dir, "output")
        os.makedirs(destination_folder, exist_ok=True)
        print(f"Test-Scenarios-Folder-Path: {str(destination_folder)}")
        timestamp_folder = os.path.join(destination_folder, timestamp)
        print(f"TimeStamp Folder Path: {str(timestamp_folder)}")
        scenario_folder = os.path.join(timestamp_folder, str(scenario_id))
        print(f"Scenario Folder Path: {str(scenario_folder)}")
        screenshot_folder = os.path.join(scenario_folder, "screenshots")
        print(f"Screenshot Folder Path: {str(screenshot_folder)}")
        outputs_folder = os.path.join(script_dir, "outputs")
        self.move_png_files(outputs_folder, screenshot_folder)
        FileHandler.write_to_file(str(scenario_folder) + "/" + str(scenario_id) + ".log", str(scenario_json_data))
        FileHandler.write_to_file(str(scenario_folder) + "/" + str(scenario_id) + ".log", str(bot_data))
        FileHandler.write_to_file(str(scenario_folder) + "/" + str(scenario_id) + ".log", str(validation_result))
        DockerHandler.delete_folder_from_container(container_name, docker_source_file_folder)
        self.delete_folder(outputs_folder)
        print(f"{scenario_id}: Finished")
        return validation_result


def build_html(json_data, timestamp, execution_results):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filepath = os.path.join(script_dir, f"/output/{timestamp}/index.html".lstrip("/"))
    json_output = []
    for item in json_data:
        scenario_id = item['scenario_id']
        log_filepath = os.path.join(script_dir, f"/output/{timestamp}/{scenario_id}/{scenario_id}.log".lstrip("/"))
        json_output.append({
            'timestamp': timestamp,
            'scenario_id': scenario_id,
            'scenario_description': item['Test Scenario Description'],
            'execution_result': execution_results[item['scenario_id']],
            'screenshots': '',
            'log_url': f"file://{log_filepath}"

        })
    generate_html(json_output, output_file=output_filepath)
    webbrowser.open(f"file://{output_filepath}")


if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = os.getenv('ANTHROPIC_API_KEY')
    test_executor = TestScenarioExecutor(api_key=API_KEY)

    browser = start_chrome('http://localhost:8080')
    sleep(20)

    test_scenario_path = "test_scenario.json"
    json_data = FileHandler.read_json(test_scenario_path)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    execution_results = {}
    for item in json_data:
        output = test_executor.execute_scenario(item, timestamp)
        execution_results[item['scenario_id']] = output['scenario_tested_successfully']
        print("Test Scenario Execution Result:", output)

    kill_browser()
    build_html(json_data, timestamp, execution_results)
