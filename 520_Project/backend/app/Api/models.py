from dataclasses import dataclass, asdict
import boto3
import json
from typing import Type, TypeVar
from app.Api.enums import *
from app.Api.exceptions import *

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
# Initialize s3 client
s3_client = boto3.client('s3')


# Table names
USER_FILES_TABLE = "llm-user-files"
LLM_FILE_TABLE = "llm-file-table"
USER_TABLE = "llm-user-table"
# S3 bucket
S3_BUCKET_NAME = 'llm-query-generator'

# Type variable for generic return type in base class methods
T = TypeVar('T', bound='BaseModel')


class BaseModel:
    """
    Base class providing common methods for JSON and dictionary conversions.
    """
    def to_dict(self) -> dict:
        """
        Convert the object to a dictionary.

        Returns:
            dict: Dictionary representation of the object.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        """
        Create an object instance from a dictionary.

        Args:
            data (dict): Dictionary containing the object data.

        Returns:
            T: An instance of the class.
        """
        return cls(**data)

    def to_json(self) -> str:
        """
        Convert the object to a JSON string.

        Returns:
            str: JSON representation of the object.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls: Type[T], json_data: str) -> T:
        """
        Create an object instance from a JSON string.

        Args:
            json_data (str): JSON string containing the object data.

        Returns:
            T: An instance of the class.
        """
        data = json.loads(json_data)
        return cls.from_dict(data)


@dataclass
class User(BaseModel):
    """
    Represents a user in the USER_TABLE.

    Attributes:
        user_id (str): Unique identifier for the user.
        name (str): Full name of the user.
        username (str): Username of the user.
        email (str): Email address of the user.
    """
    user_id: str
    name: str
    username: str
    email: str = ""

    @staticmethod
    def get(user_id: str):
        """
        Retrieve a user from the USER_TABLE by user_id.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            dict: The user item from the table, or None if not found.
        """
        table = dynamodb.Table(USER_TABLE)
        response = table.get_item(Key={'user_id': user_id})
        return response.get('Item')

    def put(self):
        """
        Insert or update the user in the USER_TABLE.
        """
        table = dynamodb.Table(USER_TABLE)
        table.put_item(Item=self.to_dict())
    
    @classmethod
    def _required_keys(cls):
        return ["username", "name", "email"]

    @staticmethod
    def validate_nd_make_user(data):
        if any([(key not in data) or (key is None) for key in User._required_keys()]):
            raise InvalidInputException("username, name and email should not be null or empty")
        return User(user_id=data['username'],name=data['name'], username=data['username'], email=data['email']), Status.VALID




@dataclass
class UserFiles(BaseModel):
    """
    Represents the files owned by a user in the USER_FILES_TABLE.

    Attributes:
        user_id (str): Unique identifier for the user.
        files (list): List of files owned by the user.
        file structure: {
            'file_id': <file_id>,
            'filename': <filename>,
            'size': <file-size-kb>
        }
    """
    user_id: str
    files: list

    @staticmethod
    def get(user_id: str):
        """
        Retrieve user files from the USER_FILES_TABLE by user_id.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            dict: The user files item from the table, or None if not found.
        """
        table = dynamodb.Table(USER_FILES_TABLE)
        response = table.get_item(Key={'user_id': user_id})
        return response.get('Item')

    def put(self):
        """
        Insert or update the user's files in the USER_FILES_TABLE.
        """
        table = dynamodb.Table(USER_FILES_TABLE)
        table.put_item(Item=self.to_dict())

#  can remove this
@dataclass
class LLMFile(BaseModel):
    """
    Represents a file in the LLM_FILE_TABLE.

    Attributes:
        file_id (str): Unique identifier for the file.
        file_name (str): Name of the file.
        metadata (dict): Additional metadata about the file.
    """
    file_id: str
    file_name: str
    metadata: dict

    # @staticmethod
    # def get(file_id: str):
    #     """
    #     Retrieve a file from the LLM_FILE_TABLE by file_id.

    #     Args:
    #         file_id (str): The unique identifier of the file.

    #     Returns:
    #         dict: The file item from the table, or None if not found.
    #     """
    #     table = dynamodb.Table(LLM_FILE_TABLE)
    #     response = table.get_item(Key={'file_id': file_id})
    #     return response.get('Item')

    # def put(self):
    #     """
    #     Insert or update the file in the LLM_FILE_TABLE.
    #     """
    #     table = dynamodb.Table(LLM_FILE_TABLE)
    #     table.put_item(Item=self.to_dict())


# Example usage
# if __name__ == '__main__':
#     # Example user
#     user = User(user_id='123', name='John Doe', username='johndoe', email='john.doe@example.com')
#     user.put()  # Insert into USER_TABLE
#     print("User retrieved:", User.get('123'))
#     print("User JSON:", user.to_json())

#     # Example user files
#     user_files = UserFiles(user_id='123', file_ids=['file1', 'file2'])
#     user_files.put()  # Insert into USER_FILES_TABLE
#     print("User files retrieved:", UserFiles.get('123'))
#     print("UserFiles JSON:", user_files.to_json())

#     # Example LLM file
#     llm_file = LLMFile(file_id='file1', file_name='sample.txt', metadata={'size': '10KB'})
#     llm_file.put()  # Insert into LLM_FILE_TABLE
#     print("LLM file retrieved:", LLMFile.get('file1'))
#     print("LLMFile JSON:", llm_file.to_json())
