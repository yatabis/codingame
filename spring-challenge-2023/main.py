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
    log(*cells, sep="\n")
    n_bases = int(input())
    my_bases = {int(input()) for _ in range(n_bases)}
    opp_bases = {int(input()) for _ in range(n_bases)}

    distances = [-1] * n_cells
    base_id = -1
    todo = deque()
    for i in my_bases:
        todo.append((i, 0))
        base_id = i
    while todo:
        i, d = todo.popleft()
        if distances[i] != -1:
            continue
        distances[i] = d
        for j in cells[i].neighbors:
            if j != -1:
                todo.append((j, d + 1))
    log(distances)
    nearest_cells = [cell.id for cell in sorted(cells, key=lambda cell: distances[cell.id])]
    log(nearest_cells)

    # Game loop
    while True:
        for i in range(n_cells):
            cells[i].update(*map(int, input().split()))
        for i in nearest_cells:
            cell = cells[i]
            if cell.resources > 0:
                print(f"LINE {base_id} {cell.id} 1")
                break
        else:
            print("WAIT")


if __name__ == '__main__':
    main()
