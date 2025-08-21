class ApiError(Exception):
    pass

class SettingsError(ApiError):
    pass

class DataBaseError(ApiError):
    pass

class ConnectionError(ApiError):
    pass

class ResponseError(ConnectionError):
    pass

class RequestError(ConnectionError):
    pass
