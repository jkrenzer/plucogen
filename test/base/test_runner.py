import unittest


class LogCaptureResult(unittest._TextTestResult):
    """Log capturing result class inspired by @clayg"""

    def _exc_info_to_string(self, err, test):
        # jack into the bit that writes the tracebacks, and add captured log
        tb = super(LogCaptureResult, self)._exc_info_to_string(err, test)
        captured_log = test.stream.getvalue()
        return "\n".join(
            [tb, "Captured logging (most recent call last):", "-" * 70, captured_log]
        )


class TestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        # be nice if TextTestRunner just had a class attr for defaultResultClass
        return LogCaptureResult(self.stream, self.descriptions, self.verbosity)
