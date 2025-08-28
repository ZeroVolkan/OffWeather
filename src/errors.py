class GeneralError(Exception):
    pass


# General Errors for api
class ApiError(GeneralError):
    pass


# Error for class ConfigAPI from api.py
class ConfigError(ApiError):
    pass


# Endpoint Error
class EndpointError(ApiError):
    pass


# General Errors for Service
class ServiceError(GeneralError):
    pass


class ProcessorError(ServiceError):
    pass


class DataBaseError(ServiceError):
    pass


# Connection Errors
class ConnectionError(GeneralError):
    pass


class ResponseError(ConnectionError):
    pass


class RequestError(ConnectionError):
    pass


# Other Errors
# Error for file setting.py
class SettingError(Exception):
    pass
