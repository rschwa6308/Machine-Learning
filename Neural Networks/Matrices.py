class Matrix:
    def __init__(self, array):
        self.array = array
        self.height = len(array)
        self.width = len(array[0])

    def __repr__(self):
        max_spacing = len(str(max([max(row) for row in self.array])))
        return "│" + "│\n│".join(
            [" ".join([(str(n) + " " * 30)[:max_spacing] for n in row]) for row in self.array]) + "│"

    def __add__(self, other):
        return Matrix([[self.array[y][x] + other.array[y][x] for x in range(self.width)] for y in range(self.height)])

    def __sub__(self, other):
        return Matrix([[self.array[y][x] - other.array[y][x] for x in range(self.width)] for y in range(self.height)])

    def __mul__(self, other):
        if isinstance(other, Matrix):  # Matrix Multiplication
            return Matrix(
                [[sum([self.array[y][n] * other.array[n][x] for n in range(self.width)])
                  for x in range(other.width)]
                 for y in range(self.height)]
            )
        else:  # Scalar Multiplication
            return Matrix([[n * other for n in row] for row in self.array])


if __name__ == "__main__":
    a = Matrix([[3, 4, 2]])
    b = Matrix([[13, 9, 7, 15], [8, 7, 4, 6], [6, 4, 0, 3]])

    print("b * 2 = ")
    print(b * 2, "\n")
    print("a + b = ")
    print(a + b, "\n")
    print("a * b = ")
    print(a * b, "\n")
