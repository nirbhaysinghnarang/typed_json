class DeserializeException(Exception):
    """ 
    Raised when there is an error in destructuring a JSON string and initializing a class
    """
    def __init__(self, msg):
        super().__init__(msg)
