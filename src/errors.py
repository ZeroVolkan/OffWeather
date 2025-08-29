class GeneralError(Exception):
    pass


class ConfigError(GeneralError):
    pass


class CommandError(GeneralError):
    pass


# General Errors for api
class ApiError(GeneralError):
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
