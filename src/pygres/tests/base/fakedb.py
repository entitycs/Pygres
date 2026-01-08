class FakeDB:
    """
    A fake DB adapter that captures SQL and parameters.
    """
    def __init__(self):
        self.last_sql = None
        self.last_params = None

    def execute(self, sql, params=None):
        self.last_sql = sql
        self.last_params = params

    def fetch_val(self, sql, params=None):
        self.last_sql = sql
        self.last_params = params
        return 42  # pretend DB assigned ID 42
