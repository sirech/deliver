import unittest
import os

def get_suite():
    all_names = []
    for path, _, names in os.walk(os.path.dirname(__file__)):
        names = ["%s.%s" % (get_package(path), m[:-3])
                 for m in names
                 if m.startswith("test_") and m.endswith(".py")]
        all_names += names
    suite = unittest.TestLoader().loadTestsFromNames(all_names)
    return suite

def get_package(path):
    elements = []
    path, package = os.path.split(path)
    while package != 'deliver':
        elements.append(package)
        path, package = os.path.split(path)
    elements.append('deliver')
    return '.'.join(reversed(elements))

test_suite = get_suite()

def main():
    unittest.TextTestRunner().run(test_suite)

if __name__ == "__main__":
    main()
