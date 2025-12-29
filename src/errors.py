class GeneralError(Exception): ...


# General Errors for api
class APIError(GeneralError): ...


class EndpointError(APIError): ...


class DataError(APIError): ...


class RepositoryError(APIError): ...


class ConfigError(APIError): ...  # For ConfigAPI class


# Connection Errors
class ConnectionError(GeneralError): ...


class ResponseError(ConnectionError): ...


class RequestError(ConnectionError): ...


# Error for class Setting from file setting.py.
class SettingError(Exception):
    pass
