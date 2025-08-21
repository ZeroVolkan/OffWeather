class ApiError(Exception):
    pass


class UnknownApiError(ApiError):
    pass


class SettingsError(ApiError):
    pass


class ConfigError(SettingsError):
    pass


class EndpointError(ApiError):
    pass


class ProcessorError(ApiError):
    pass


class DataBaseError(ApiError):
    pass


class ConnectionError(ApiError):
    pass


class ResponseError(ConnectionError):
    pass


class RequestError(ConnectionError):
    pass
