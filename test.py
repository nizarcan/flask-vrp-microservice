import unittest
import json
from controllers.solver import vrp_solver
from errors import InvalidInputError, NoSolutionError

def read_json(file_path):
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)

def get_input_output(file_name):
    file_path = "data/{}/" + file_name + ".json"
    input_data = read_json(file_path.format("input"))
    wanted_solution = read_json(file_path.format("output"))
    return input_data, wanted_solution

class TestVRP(unittest.TestCase):

    def test_sample_input(self):
        input_data, wanted_solution = get_input_output("sample")
        self.assertEqual(vrp_solver(input_data), wanted_solution, "Sample input's solution should match with saved json.")

    def test_with_10_orders(self):
        input_data, wanted_solution = get_input_output("10_orders")
        self.assertEqual(vrp_solver(input_data), wanted_solution, "Sample input's solution should match with saved json.")

    def test_with_50_orders(self):
        input_data, wanted_solution = get_input_output("50_orders")
        self.assertEqual(vrp_solver(input_data), wanted_solution, "Sample input's solution should match with saved json.")

    def test_infeasible_problem(self):
        input_data, _ = get_input_output("infeasible")
        with self.assertRaises(NoSolutionError):
            vrp_solver(input_data)

    def test_invalid_input(self):
        input_data, _ = get_input_output("invalid_structure")
        with self.assertRaises(InvalidInputError):
            vrp_solver(input_data)


if __name__ == '__main__':
    t = unittest.TestLoader().loadTestsFromTestCase(TestVRP)
    unittest.TextTestRunner(verbosity=2).run(t)
