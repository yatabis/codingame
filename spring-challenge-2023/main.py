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
    target_cell = base_id
    while True:
        my_ants, opp_ants = 0, 0
        for i in range(n_cells):
            r, my, opp = map(int, input().split())
            cells[i].update(r, my, opp)
            my_ants += my
            opp_ants += opp
        target_type = 0
        if my_ants < opp_ants * 0.9:
            target_type = 1
        elif my_ants > opp_ants * 1.1:
            target_type = 2
        log(my_ants, opp_ants, target_type)
        if target_cell is None or cells[target_cell].resources <= 0:
            for i in nearest_cells[target_cell]:
                if cells[i].resources <= 0:
                    continue
                if target_type == 1 and cells[i].type !=1:
                    continue
                if target_type == 2 and cells[i].type != 2:
                    continue
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
