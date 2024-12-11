class P3ValueError(Exception):
    pass


class P3CommError(Exception):
    pass


class P3DevError(Exception):
    def __init__(self, err_code=0, err_code_ext=0):
        self.err_code = err_code
        self.err_code_ext = err_code_ext