class Cell:
    def __init__(self, i, t, r):
        self.id = i
        self.type = t
        self.resources = r


def main():
    # Initial inputs
    n_cells = int(input())
    cells = []
    for i in range(n_cells):
        t, r, *_ = map(int, input().split())
        cells.append(Cell(i, t, r))
    n_bases = int(input())
    my_bases = {int(input()) for _ in range(n_bases)}
    opp_bases = {int(input()) for _ in range(n_bases)}

    # Game loop
    while True:
        for i in range(n_cells):
            resources, my_ants, opp_ants = map(int, input().split())
        print("WAIT")


if __name__ == '__main__':
    main()
