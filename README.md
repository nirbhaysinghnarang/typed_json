# TypedJSON

`TypedJSON` is a Python class that enables the deserialization of JSON data into an object of a specified type with type safety and verification.

## Features

- Deserialize JSON data into an object of a specified type.
- Verify that JSON data is compatible with the object's initializer signature.
- Handle nested objects and complex data structures.
- Serialize an instance of a class back to a JSON string.

## Installation

You can use `TypedJSON` by including running 
```python
pip install json-typed==0.1.1
```

## Usage

1. Import the `TypedJSON` class and the `DeserializeException` exception:

    ```python
    from typed_json import TypedJSON, DeserializeException
    ```

2. Define your Python classes that represent the data structure you want to deserialize from JSON.

    ```python
    class Street:
        def __init__(self, name: str, pos: int):
            self.name = name
            self.pos = pos

    class Address:
        def __init__(self, street: Street):
            self.street = street

    class Person:
        def __init__(self, name: str, age: int, add: Address):
            self.name = name
            self.age = age
            self.address = add
    ```

3. Create a `TypedJSON` instance with the target type:

    ```python
    typed_json = TypedJSON(Person)
    ```

4. Use the `load` method to deserialize JSON data into an object of the specified type:

    ```python
    json_data = '{"name": "John", "age": 30, "add": {"street": {"name": "123 Main St", "pos": 42}}}'
    try:
        person_obj = typed_json.load(json_data)
        print(person_obj.name)
        print(person_obj.age)
    except DeserializeException as e:
        print(f"Deserialization error: {str(e)}")
    ```

5. Use the `dumps` method to serialize an object back to a JSON string:

    ```python
    serialized_json = typed_json.dumps(person_obj)
    print(serialized_json)
    ```

## Error Handling

`TypedJSON` raises a `DeserializeException` if there are issues during deserialization. You can catch this exception to handle errors gracefully.

## Contribution

Contributions are welcome! If you find issues or have suggestions for improvements, please open an issue or create a pull request on the GitHub repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
