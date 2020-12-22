from requests import Response


class ConohaException(Exception):
    """
    ConohaAppの例外の基底クラス
    """
    pass


class ConohaRequestsException(ConohaException):
    def __init__(self, message: str, is_retry: bool, response: Response = None):
        self.message = message
        self.is_retry = is_retry
        self.response = response
        super().__init__(message)


class ConohaUploadException(ConohaException):
    pass


class ConohaNotSpecifiedException(ConohaException):
    pass
