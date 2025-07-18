import json
import logging
import os

response_path = "responses.json"
result_path = "results.json"
user_path = "users.json"

def get_responses():
    # Read existing data from the JSON file if it exists
    if os.path.exists(response_path):
        with open(response_path, "r") as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    return existing_data

def save_response(responses):
    data = get_responses()

    # Append the new response data to the existing data
    data.extend(responses)

    # Write the updated data back to the JSON file
    with open(response_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

def update_response(responses):
    with open(response_path, "w") as json_file:
        json.dump(responses, json_file, indent=4)

def delete_response(id):
    responses = get_responses()

    data = None
    updated_responses = []
    # Filter out the response with the matching __PowerAppsId__
    for response in responses:
        if response.get("__PowerAppsId__") == id:
            data = response
        else:
            updated_responses.append(response)

    # If the length of updated_responses is less than the original, then we have deleted an entry
    logging.info(f"length updated_response: {len(updated_responses)}, length responses: {len(responses)}")
    if len(updated_responses) < len(responses):
        # Save the updated list back to the file
        update_response(updated_responses)
        logging.info(f"Response with ID {id} has been deleted.")
    else:
        logging.warning(f"No response found with ID {id}.")

    return data

def get_users():
    # Read existing data from the JSON file if it exists
    if os.path.exists(user_path):
        with open(user_path, "r") as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    return existing_data

def get_user(name):
    users = get_users()

    if name not in users:
        return None

    return users[name]

def get_value(data, key, default_value=None):
    if data:
        if data[key]:
            return data[key]
        else:
            return default_value

    if default_value:
        return default_value

    return None

def get_results():
    # Read existing data from the JSON file if it exists
    if os.path.exists(result_path):
        with open(result_path, "r") as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    return existing_data

def get_result(id):
    results = get_results()

    if id not in results:
        return None

    return results[id]

def save_result(response, ticket_number=None):
    data = get_results()

    response["key"] = ticket_number
    if ticket_number:
        response["status"] = "To Do"
    # Append the new response data to the existing data
    data[response["__PowerAppsId__"]] = {key: value for key, value in response.items() if key != "__PowerAppsId__"}

    # Write the updated data back to the JSON file
    with open(result_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

def update_result_status(id, status):
    results = get_results()

    if id not in results:
        logging.warning(f"Result with ID {id} not found.")
        return None

    results[id]["status"] = status

    # Write the updated data back to the JSON file
    with open(result_path, "w") as json_file:
        json.dump(results, json_file, indent=4)

    logging.info(f"Result with ID {id} has been updated to status '{status}'.")

def delete_result(id):
    results = get_results()

    if id not in results:
        logging.warning(f"Result with ID {id} not found.")
        return None

    del results[id]

    # Write the updated data back to the JSON file
    with open(result_path, "w") as json_file:
        json.dump(results, json_file, indent=4)

    logging.info(f"Result with ID {id} has been deleted.")
    return id