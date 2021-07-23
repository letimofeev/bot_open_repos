class GoogleDriveError(Exception):
    pass


class GDExistError(GoogleDriveError):
    def __init__(self, msg):
        self.msg = msg


class GDFolderError(GoogleDriveError):
    def __init__(self, msg):
        self.msg = msg


class GDConnection(GoogleDriveError):
    def __init__(self, msg):
        self.msg = msg


class WolframalphaError(Exception):
    pass
