from collections import deque
import sys


def log(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)


class Cell:
    def __init__(self, i, t, r, neigh):
        self.id = i
        self.type = t
        self.resources = r
        self.neighbors = neigh
        self.my_ants = 0
        self.opp_ants = 0

    def update(self, r, my, opp):
        self.resources = r
        self.my_ants = my
        self.opp_ants = opp

    def __str__(self):
        return f"Cell(id={self.id}, type={self.type}, resources={self.resources}, neighbors={self.neighbors})"


def main():
    # Initial inputs
    n_cells = int(input())
    cells = []
    for i in range(n_cells):
        t, r, *neigh = map(int, input().split())
        cells.append(Cell(i, t, r, neigh))
    n_bases = int(input())
    my_bases = {int(input()) for _ in range(n_bases)}
    opp_bases = {int(input()) for _ in range(n_bases)}
    base_id = list(my_bases)[0]

    # Compute distances
    distances = [[-1] * n_cells for _ in range(n_cells)]
    for i in range(n_cells):
        todo = deque()
        todo.append((i, 0))
        while todo:
            j, d = todo.popleft()
            if distances[i][j] != -1:
                continue
            distances[i][j] = d
            for k in cells[j].neighbors:
                if k != -1:
                    todo.append((k, d + 1))
    nearest_cells = [[cell.id for cell in sorted(cells, key=lambda cell: distances[i][cell.id])] for i in range(n_cells)]

    # Game loop
    target = base_id
    while True:
        for i in range(n_cells):
            cells[i].update(*map(int, input().split()))
        if not target or cells[target].resources <= 0:
            for i in nearest_cells[target]:
                if cells[i].resources > 0:
                    target = i
                    break
            else:
                target = None
        if target is not None:
            print(f"LINE {base_id} {target} 1")
        else:
            print("WAIT")


if __name__ == '__main__':
    main()
