
from datetime import time
import requests, json
import os
from powerbi_test_framework.utils.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)

class MondayClient:
    def __init__(self, api_key, api_url, file_url):
        self.board_id = None
        self.group_id = None
        self.api_key = api_key
        self.api_url = api_url
        self.file_url = file_url
        self.headers = {"Authorization": api_key, "Content-Type": "application/json"}
        logger.info("MondayClient initialized.")

    def _execute(self, query, variables=None, retries=3):
        """Centralized executor for GraphQL queries/mutations with retry + logging."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        for attempt in range(1, retries + 1):
            try:
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    data=json.dumps(payload),
                    timeout=10
                )

                if response.status_code != 200:
                    raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

                data = response.json()

                # Handle Monday GraphQL errors
                if "errors" in data:
                    logger.error(f"Monday API Error: {data['errors']}")
                    return None

                return data.get("data")

            except requests.Timeout:
                logger.warning(f"Timeout on attempt {attempt}/{retries}. Retrying...")
            except requests.RequestException as e:
                logger.error(f"RequestException: {e}")
                time.sleep(2)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break

        logger.error("All retry attempts failed.")
        return None

    def create_or_update_columns(self):
        logger.info("Creating or updating columns.")


        """Ensure all standard columns exist on the board; create missing ones."""
        column_defs = [
            {"title": "Test Date", "type": "date"},
            {"title": "Environment", "type": "text"},
            {"title": "Total Tests", "type": "numbers"},
            {"title": "Passed Tests", "type": "numbers"},
            {"title": "Failed Tests", "type": "numbers"},
            {"title": "Skipped Tests", "type": "numbers"},
            {"title": "Pass Rate (%)", "type": "numbers"},
            {"title": "Duration", "type": "text"},
            # {"title": "Status", "type": "status"},
            {"title": "Summary", "type": "long_text"},
        ]


        # Fetch current columns
        query = f"""query {{ boards (ids: {self.board_id}) {{ columns {{ id title type }} }} }}"""
        data = self._execute(query)
        existing_columns = {col["title"]: col["id"] for col in data["boards"][0]["columns"]}

        for col in column_defs:
            title = col["title"]
            if title not in existing_columns:
                logger.info(f"Adding missing column: {title}")
                mutation = f"""
                            mutation {{
                            create_column (
                                board_id: {self.board_id},
                                title: "{col['title']}",
                                column_type: {col['type']}
                            ) {{
                                id
                                title
                            }}
                            }}
                            """

                try:
                    res = self._execute(mutation)
                    logger.info(f"Created column: {res['create_column']['title']}")
                except Exception as e:
                    logger.error(f"Error creating column '{title}': {e}")


            else:
                logger.info(f"Column already exists: {title}")

        mutation =  f"""
                    mutation {{
                    create_status_column(
                    board_id: {self.board_id},
                    id: "project_status",
                    title: "Status",
                    defaults: {{
                    labels: [
                        {{ color: stuck_red, label: "Pending", index: 2}},
                        {{ color: done_green, label: "Completed", index: 1}},
                    ]
                    }},
                    description: "The project's status."
                ) {{
                    description
                    id
                    title
                }}
                }}"""

        res = self._execute(mutation)

    def get_or_create_board(self, board_name):
        """Retrieve existing board ID by name or create a new one."""
        logger.info(f"Getting or creating board: {board_name}")
        query = """query { boards { id name } }"""
        data = self._execute(query)
        if data:
            for board in data["boards"]:
                if board["name"] == board_name:
                    self.board_id = board["id"]
                    # self.create_or_update_columns()
                    # res = self.create_dashboard("Automation Test Dashboard")

                    logger.info(f"Found existing board: {board_name} ({self.board_id})")
                    return board["id"]

        # Board not found, create it
        logger.info(f"Board not found, creating new board: {board_name}")
        mutation = f"""mutation {{ create_board (board_name: "{board_name}", board_kind: public) {{ id }} }}"""
        data = self._execute(mutation)
        if data:
            self.board_id = data["create_board"]["id"]
            self.create_or_update_columns()
            # res = self.create_dashboard("Automation Test Dashboard")
            # logger.info(f"Created new board: {board_name} ({self.board_id})")
            return self.board_id
        return None

    def get_columns(self):
        logger.info("Getting columns.")
        query = f"""
        query {{
        boards (ids: {self.board_id}) {{
            columns {{
            id
            title
            type
            }}
        }}
        }}
        """
        data = self._execute(query)
        if data:
            return data["boards"][0]["columns"]
        return []

    def get_subitem_board_id(self):
        """
        Fetch and return the subitem board ID for the given parent board.
        """
        query = f"""
        query {{
          boards(ids: [{self.board_id}]) {{
              columns {{
               id 
               title 
               type 
               settings_str 
               }} 
            }} 
        }}
        """

        data = self._execute(query)

        subitems = data["boards"][0]["columns"]
        for sub_item in subitems:
            if sub_item.get("settings_str") and sub_item.get("title") == "Subitems":
                settings = json.loads(sub_item["settings_str"])
                subitem_board_ids = settings.get("boardIds", [])
                if subitem_board_ids:
                    return subitem_board_ids[0]
        if not subitems:
            logger.warning(f"No subitems found for board ID: {self.board_id}")
            return None

    def get_subitem_by_name(self, item_id, sub_item_name):
        """
        Fetch subitems by the given sub item name
        """
        query = f"""
        query  {{
          items(ids: {item_id}) {{
            subitems {{
              id
              name
              column_values {{
                id
                text
                value
              }}
            }}
          }}
        }}
        """

        data = self._execute(query)
        if data:
            item_name = data["items"][0]["subitems"]
            for item in item_name:
                if item["name"] == sub_item_name:
                    logger.info(f"Found sub item: {sub_item_name} ({item['id']})")
                    return item["id"]
        logger.info(f"Sub Item not found: {sub_item_name}")
        return None

    def get_or_create_group(self, group_name):
        logger.info(f"Getting or creating group: {group_name}")
        query = f"""query {{ boards (ids: {self.board_id}) {{ groups {{ id title }} }} }}"""
        data = self._execute(query)
        if data:
            for group in data["boards"][0]["groups"]:
                if group["title"] == group_name:
                    self.group_id = group["id"]
                    logger.info(f"Found existing group: {group_name} ({self.group_id})")
                    return group["id"]

        logger.info(f"Group not found, creating new group: {group_name}")
        mutation = f"""mutation {{ create_group (board_id: {self.board_id}, group_name: "{group_name}") {{ id }} }}"""
        data = self._execute(mutation)
        if data:
            self.group_id = data["create_group"]["id"]
            logger.info(f"Created new group: {group_name} ({self.group_id})")
            return self.group_id
        return None

    def get_item_id_by_name(self, item_name):
        logger.info(f"Getting item ID by name: {item_name}")
        query = f"""
        query {{
        boards (ids: {self.board_id}) {{
            items_page (limit: 100) {{
            items {{
                id
                name
            }}
            }}
        }}
        }}
        """
        data = self._execute(query)
        if data:
            items = data["boards"][0]["items_page"]["items"]
            for item in items:
                if item["name"] == item_name:
                    logger.info(f"Found item: {item_name} ({item['id']})")
                    return item["id"]
        logger.info(f"Item not found: {item_name}")
        return None

    def create_item(self, group_id, item_name, column_values):
        """
        Create an item on Monday.com with properly encoded column_values.
        """
        logger.info(f"Creating item: {item_name}")
        # Make sure board_id is a string, not int
        board_id_str = str(self.board_id)

        # Properly escape JSON for GraphQL
        col_values_json = json.dumps(column_values)
        col_values_json = json.dumps(column_values).replace('"', '\\"')

        mutation = f"""
        mutation {{
        create_item(
            board_id: {board_id_str},
            group_id: "{group_id}",
            item_name: "{item_name}",
            column_values: "{col_values_json}"
        ) {{
            id
        }}
        }}
        """

        response = self._execute(mutation)

        # Debugging and safety checks
        if not response:
            logger.error("Monday API Error (create_item): No response")
            return None

        item_id = response["create_item"]["id"]
        logger.info(f"Item created successfully: {item_id}")
        return item_id

    def create_sub_item(self, item_id, item_name, column_values):

        query = """
        mutation ($parent_item_id: ID!, $item_name: String!, $column_values: JSON!) {
          create_subitem(
            parent_item_id: $parent_item_id,
            item_name: $item_name,
            column_values: $column_values
          ) {
            id
            name
            board {
              id
              name
            }
          }
        }
        """

        # Convert dict to JSON string
        col_values_json = json.dumps(column_values)

        variables = {
            "parent_item_id": str(item_id),
            "item_name": item_name,
            "column_values": col_values_json  # must be string!
        }

        response = self._execute(query, variables)
        if not response:
            logger.error("Monday API Error (create_item): No response")
            return None

        sub_item_id = response["create_subitem"]["id"]

        return  sub_item_id

    def update_item(self, item_id, column_values):
        """
        Update an existing item on Monday.com with new column_values.
        """
        logger.info(f"Updating item: {item_id}")

        item_id_str = str(item_id)
        # Properly escape JSON for GraphQL
        col_values_json = json.dumps(column_values).replace('"', '\\"')

        mutation = f"""
        mutation {{
        change_multiple_column_values(
            item_id: {item_id_str},
            board_id: {self.board_id},
            column_values: "{col_values_json}"
        ) {{
            id
        }}
        }}
        """

        response = self._execute(mutation)

        # Debugging and safety checks
        if not response:
            logger.error("Monday API Error (update_item): No response")
            return None

        logger.info(f"Item updated successfully: {item_id}")
        return response["change_multiple_column_values"]["id"]

    def update_subitem(self, subitem_board_id, item_id, column_values):
        """
        Update an existing item on Monday.com with new column_values.
        """
        logger.info(f"Updating item: {item_id}")

        item_id_str = str(item_id)
        # Properly escape JSON for GraphQL
        col_values_json = json.dumps(column_values).replace('"', '\\"')

        mutation = f"""
        mutation {{
        change_multiple_column_values(
            item_id: {item_id_str},
            board_id: {subitem_board_id},
            column_values: "{col_values_json}"
        ) {{
            id
        }}
        }}
        """

        response = self._execute(mutation)

        # Debugging and safety checks
        if not response:
            logger.error("Monday API Error (update_item): No response")
            return None

        logger.info(f"Item updated successfully: {item_id}")
        return response["change_multiple_column_values"]["id"]

    def create_update(self, item_id, text):
        logger.info(f"Creating update for item: {item_id}")

        safe_text = json.dumps(text)
        mutation = f"""
        mutation {{
          create_update (item_id: {item_id}, body: {safe_text}) {{
            id
          }}
        }}
        """
        data = self._execute(mutation)
        if data:
            logger.info(f"Created update for item ID: {item_id}")
            return data["create_update"]["id"]
        return None

    def get_subitem_columns(self, subitem_board_id):
        """
        Fetch all columns (id, title, type) for a subitem board.
        """
        query = f"""
        query {{
          boards(ids: [{subitem_board_id}]) {{
            id
            name
            columns {{
              id
              title
              type
            }}
          }}
        }}
        """
        data = self._execute(query)
        try:
            columns = data["boards"][0]["columns"]
            logger.info(f"Found {len(columns)} columns for subitem board {subitem_board_id}")
            return columns
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error fetching subitem columns: {e}")
            return []

    def upload_file(self, item_id, file_path, column_id):
        """Upload all HTML report files in a folder to a specific Monday.com update."""
        logger.info(f"Uploading report files from '{file_path}' to item ID: {item_id}")

        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            logger.error(f"File not found: {abs_path}")
            return None

        logger.info(f"Uploading file '{abs_path}' to item {item_id} column {column_id}")

        # GraphQL mutation for uploading file
        query = """
                  mutation ($file: File!) {
                    add_file_to_column(item_id: ITEM_ID, column_id: "COLUMN_ID", file: $file) {
                      id
                      name
                      url
                    }
                  }
                  """.replace("ITEM_ID", str(item_id)).replace("COLUMN_ID", column_id)

        headers = {"Authorization": self.api_key}

        # File upload requires multipart/form-data with query + variables[file]
        with open(abs_path, "rb") as file_data:
            files = {
                "query": (None, query),
                "variables[file]": (os.path.basename(abs_path), file_data, "application/octet-stream"),
            }

            response = requests.post(self.file_url, headers=headers, files=files)

        # Parse response
        try:
            resp_json = response.json()
        except Exception as e:
            logger.error(f"Error parsing upload response: {e}")
            resp_json = {"error": str(e), "raw": response.text}

        if response.status_code != 200 or "errors" in resp_json:
            logger.error(f"Upload failed: {resp_json}")
            return None

        result = resp_json.get("data", {}).get("add_file_to_column")
        logger.info(f"Uploaded file successfully: {result}")
        return result

    def get_all_users(self, users, limit=100):
        """
        Get all users (active + invited/pending) in the Monday.com account.
        """
        query = f"""
           query {{
             users(kind: all, limit: {limit}) {{
               id
               name
               email
               is_guest
               is_pending
             }}
           }}
           """

        response = self._execute(query)

        if not response or "users" not in response:
            logger.error("Failed to fetch users from Monday API.")
            return {}

        all_users = response["users"]
        people_ids = []

        for email in users:
            for user in all_users:
                if user["email"].lower() == email.lower():
                    people_ids.append(user["id"])
                    logger.info(f"Matched {email}  ID {user['id']}")
                    break
            else:
                logger.warning(f"User with email '{email}' not found.")

        return people_ids

    def clear_file_column(self, board_id, item_id, column_id):
        """
        Clear (remove) all files from a file column in Monday.com.

        """

        logger.info(f"Clearing all files from item {item_id}, column '{column_id}'")

        query = f"""
        mutation {{
          change_column_value(
            board_id: {board_id}
            item_id: {item_id}
            column_id: "{column_id}"
            value: "{{\\\"clear_all\\\": true}}"
          ) {{
            id
          }}
        }}
        """
        response = self._execute(query)
        return response
    


    def get_all_subitems(self, parent_item_id, column_id=None):
        
        # Calculate the retention date (7 days ago)
        today = datetime.today()
        retention_date = today - timedelta(days=7)
 
        # Get the date in YYYY-MM-DD format
        retention_date_str = retention_date.strftime("%Y-%m-%d")
 
        logger.info(f"Retention date: {retention_date_str}")

        """
        Fetch all subitems for a given parent item ID.
        """
        query = f"""
                query {{
                items(ids: {parent_item_id}) {{
                    subitems {{
                    id
                    name
                    column_values(ids: ["{column_id}"]) {{
                        id
                        type
                        text
                    }}
                    }}
                }}
                }}
                """

        data = self._execute(query)
        print("subitems data:",data)

        if data and data.get("items") and data["items"][0].get("subitems"):
            subitems = data["items"][0]["subitems"] 

            logger.info(f"Found {len(subitems)} subitems for parent item ID: {parent_item_id}")

            retention_date_dt = datetime.strptime(retention_date_str, "%Y-%m-%d").date()

            expired_items = []  # store subitems that need deletion

            for subitem in subitems:
                for col in subitem["column_values"]:
                    if col["text"]:  # ensure date exists
                        subitem_date = datetime.strptime(col["text"], "%Y-%m-%d").date()
                        print(f"Subitem ID: {subitem['id']} | Name: {subitem['name']} | Date: {subitem_date}")

                        if subitem_date < retention_date_dt:
                            logger.info(f"Subitem {subitem['id']} is older than retention period -> marked for delete")
                            expired_items.append(subitem['id'])
                        else:
                            logger.info(f"Subitem {subitem['id']} is within retention period")
                    else:
                        logger.info(f"Subitem {subitem['id']} has no date field")

            return expired_items   # return list instead of single item

        logger.info(f"No subitems found for parent item ID: {parent_item_id}")
        return []

    def delete_old_sub_items(self, subitem_ids=[]):
        """Deletes items older than the retention date (7 days ago)."""
        logger.info("Starting deletion of old items.")

            
        mutation_parts = [
            f"delete_{i}: delete_item(item_id: {item_id}) {{ id }}"
            for i, item_id in enumerate(subitem_ids)
        ]

        # Join the delete operations into one mutation block
        mutation_body = "\n".join(mutation_parts)

        # MUST be a plain string, not a dict
        query = f"mutation {{\n{mutation_body}\n}}"

        print("\nFinal mutation query:\n", query)

        # Execute
        response = self._execute(query)
        if response:
            logger.info(f"Deleted {len(subitem_ids)} old items successfully.")
            return True

    def delete_item(self, item_id):
        """Delete an item based on item_id."""
        logger.info(f"Deleting item with ID: {item_id}")
 
        mutation = f"""
        mutation {{
          delete_item (item_id: {item_id}) {{
            id
          }}
        }}
        """
 
        response = self._execute(mutation)
 
        if not response:
            logger.error(f"Failed to delete item with ID: {item_id}")
            return None
 
        logger.info(f"Item with ID: {item_id} deleted successfully.")
        return response["delete_item"]["id"]
 
    # def upload_report(self, file_path, column_id):
    #     """Upload report file after deleting old records."""
    #     logger.info("Starting file upload process.")
    #     # First, delete old items
 
    #     # Proceed to upload the new report after deletion
    #     self.upload_file(file_path, column_id)
 
    # def upload_file(self, file_path, column_id):
    #     """Upload the file to a specific column."""
    #     logger.info(f"Uploading file '{file_path}' to column {column_id}")
 
    #     abs_path = os.path.abspath(file_path)
    #     if not os.path.exists(abs_path):
    #         logger.error(f"File not found: {abs_path}")
    #         return None
 
    #     query = """
    #               mutation ($file: File!) {
    #                 add_file_to_column(item_id: ITEM_ID, column_id: "COLUMN_ID", file: $file) {
    #                   id
    #                   name
    #                   url
    #                 }
    #               }
    #               """.replace("ITEM_ID", str(self.board_id)).replace("COLUMN_ID", column_id)
 
    #     headers = {"Authorization": self.api_key}
 
    #     # File upload requires multipart/form-data with query + variables[file]
    #     with open(abs_path, "rb") as file_data:
    #         files = {
    #             "query": (None, query),
    #             "variables[file]": (os.path.basename(abs_path), file_data, "application/octet-stream"),
    #         }
 
    #         response = requests.post(self.api_url, headers=headers, files=files)
 
    #     try:
    #         resp_json = response.json()
    #     except Exception as e:
    #         logger.error(f"Error parsing upload response: {e}")
    #         resp_json = {"error": str(e), "raw": response.text}
 
    #     if response.status_code != 200 or "errors" in resp_json:
    #         logger.error(f"Upload failed: {resp_json}")
    #         return None
 
    #     result = resp_json.get("data", {}).get("add_file_to_column")
    #     logger.info(f"Uploaded file successfully: {result}")
    #     return result