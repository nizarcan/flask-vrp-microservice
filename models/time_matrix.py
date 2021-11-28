from errors import InvalidInputError


class TimeMatrix:
    def __init__(self, matrix_data):
        try:
            self.matrix = matrix_data

            # Testing if matrix is nxn
            assert all(len(row) == len(self.matrix) for row in self.matrix), "Matrix size should be equal in rows and columns"

            # Dummy node creation on the time matrix
            self.matrix = [distance_row + [0] for distance_row in self.matrix]
            self.matrix += [(len(self) + 1) * [0]]

        except Exception:
            raise InvalidInputError

    def __len__(self):
        return len(self.matrix)
