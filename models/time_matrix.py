class TimeMatrix:
    def __init__(self, matrix_data):
        self.matrix = matrix_data

        # Dummy node creation on the time matrix
        self.matrix = [distance_row + [0] for distance_row in self.matrix]
        self.matrix += [(len(self) + 1) * [0]]

    def __len__(self):
        return len(self.matrix)
