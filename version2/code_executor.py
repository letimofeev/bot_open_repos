import subprocess


class PHPExecutor:
    def __init__(self, filename):
        self.filename = filename

    def submit(self, args) -> subprocess.Popen:
        proc = subprocess.Popen(f"php {self.filename} {args}", shell=True, stdout=subprocess.PIPE)
        return proc

    def execute_code(self, args: str = "") -> str:
        proc = self.submit(args)
        script_response = proc.stdout.read()
        return script_response.decode("utf-8")

