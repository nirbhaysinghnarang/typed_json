from typing import TypeVar, Type
from deserialize_exception import DeserializeException
import inspect
import json
from collections import defaultdict

T = TypeVar('T')

class TypedJSON:
    """
    Deserialize JSON data into an object of the specified type.

    Args:
        typ (Type[T]): The type of object to deserialize to.
        json_str (str): The JSON string to deserialize.

    Raises:
        DeserializeException: If there are issues during deserialization.

    Attributes:
        typ (Type[T]): The type of object to deserialize to.
        json_str (str): The JSON string to deserialize.
        constructor_args (dict): A dictionary containing constructor arguments for deserialization.
        class_members (list): A list of members (e.g., methods and attributes) of the specified type.
        initializer_members (list): A list of initializer members (e.g., '__init__' method) of the specified type.
        initializer (function): The initializer method of the specified type.
    """

    def __init__(self, typ: Type[T]):
        """
        Initialize a TypedJSON instance.

        Args:
            typ (Type[T]): The type of object to deserialize to.
            json_str (str): The JSON string to deserialize.
        """
        self.typ = typ
        self.class_members = None
        self.initializer_members = None
     
        

    def _get_all_class_members(self):
        """Retrieve all members (methods and attributes) of the specified type."""
        self.class_members = inspect.getmembers(self.typ)

    def _fetch_initializer_members(self):
        """Fetch initializer members (__init__ method) of the specified type."""
        self.initializer_members = [
            (name, member) for name, member in self.class_members if name == '__init__'
        ]
        if len(self.initializer_members) != 1:
            raise DeserializeException(f"Type {self.typ.__class__.__name__} does not have one init method.")

    def _fetch_init_and_verify_members(self, json_str):
        """Fetch the initializer and verify members."""
        self._get_all_class_members()
        self._fetch_initializer_members()
        self.initializer = self.initializer_members[0][1]
        self.verify_members(json_str)

    def _verify_member_type(self, member: inspect.Parameter, value):
        """Verify that a value matches the expected type of a member (parameter)."""
        if not isinstance(value, member.annotation):
            try:
                TypedJSON(member.annotation).load(json.dumps(value))
            except DeserializeException as stack_exception:
                raise DeserializeException(f"Value {value} cannot be cast as {member.annotation}: {stack_exception}") from stack_exception

    def verify_members(self, json_str):
        """
        Verify that JSON data can be deserialized based on the initializer's signature.

        Raises:
            DeserializeException: If JSON data is incompatible with the initializer.
        """
        json_loaded_nv = json.loads(json_str)
        initializer_signature = inspect.signature(self.initializer)
        for parameter_name, parameter_obj in initializer_signature.parameters.items():
            if parameter_name == "self":
                continue
            if parameter_name in json_loaded_nv:
                self._verify_member_type(parameter_obj, json_loaded_nv[parameter_name])
            else:
                if parameter_obj.default == inspect._empty:
                    raise DeserializeException(f"""Parameter {parameter_name} could not be found in JSON and has no default value""")
    def load(self, json_str):
        """
        Deserialize the JSON data and create an instance of the specified type.

        Returns:
            T: An instance of the specified type with values from the JSON data.

        Raises:
            DeserializeException: If there are issues during deserialization.
        """
        self._fetch_init_and_verify_members(json_str)
        return self._deserialize(self.typ, json.loads(json_str))

    def dumps(self, obj):
        """
        Serialize an instance of the specified class to a JSON string.

        Returns:
            str: A JSON string representing the serialized object.
        """
        return self._serialize(obj)

    def _serialize(self, obj):
        """
        Recursively serialize an instance of the specified class to a JSON string.

        Args:
            cls (Type[T]): The class type of the object.
            obj (T): The object to serialize.

        Returns:
            str: A JSON string representing the serialized object.
        """
        serialized_data = {}
        class_members = inspect.getmembers(obj)
        for member_name, member_obj in class_members:
            if member_name.startswith('__'):
                continue
            if isinstance(member_obj, property):
                continue
            if hasattr(obj, member_name):
                member_value = getattr(obj, member_name)
                if any([isinstance(member_value, typ) for typ in (int, float, bool, str, list)]):
                    serialized_data[member_name] = member_value
                else:
                    serialized_data[member_name] = json.loads(TypedJSON(type(member_value)).dumps(member_value))
        return json.dumps(serialized_data)

    def _deserialize(self, cls, data):
        """
        Recursively deserialize JSON data into an object of the specified class.

        Args:
            cls (Type[T]): The class type to create from the JSON data.
            data (dict): The JSON data to deserialize.

        Returns:
            T: An instance of the specified class with values from the JSON data.

        Raises:
            DeserializeException: If there are issues during deserialization.
        """
        constructor_args = defaultdict(dict)
        initializer_signature = inspect.signature(cls.__init__)

        for parameter_name, parameter_obj in initializer_signature.parameters.items():
            if parameter_name == 'self':
                continue
            if parameter_name in data:
                value = data[parameter_name]

                if parameter_obj.annotation in (int, float, bool, str, list):
                    constructor_args[parameter_name] = value
                else:
                    nested_json_str = json.dumps(value)
                    nested_obj = TypedJSON(parameter_obj.annotation).load(nested_json_str)
                    constructor_args[parameter_name] = nested_obj
            else:
                if parameter_obj.default == inspect._empty:
                    raise DeserializeException(f"""Parameter {parameter_name} could not be found in JSON and has no default value""")
                constructor_args[parameter_name] = parameter_obj.default

        return cls(**constructor_args)






