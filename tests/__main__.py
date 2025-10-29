import unittest

class VerboseResult(unittest.TextTestResult):
    def startTest(self, test):
        # print(f"\n→ Running: {test}")
        super().startTest(test)

class VerboseRunner(unittest.TextTestRunner):
    resultclass = VerboseResult

if __name__ == "__main__":
    # Use test discovery manually to avoid the __main__ confusion
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests")

    runner = VerboseRunner(verbosity=2)
    runner.run(suite)
