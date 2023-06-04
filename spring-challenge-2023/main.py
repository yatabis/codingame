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
    my_bases = [int(i) for i in input().split()]
    opp_bases = [int(i) for i in input().split()]
    base_id = my_bases[0]

    # Compute distances
    distances = [-1] * n_cells
    parent = [-1] * n_cells
    nearset_base = [-1] * n_cells
    todo = deque([(base, 0, base, base) for base in my_bases])
    while todo:
        i, d, p, b = todo.popleft()
        if distances[i] != -1:
            continue
        distances[i] = d
        parent[i] = p
        nearset_base[i] = b
        for j in cells[i].neighbors:
            if j != -1:
                todo.append((j, d + 1, i, b))
    nearest_cells = [cell.id for cell in sorted(cells, key=lambda cell: distances[cell.id])]

    # Game loop
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
        beacons = set()
        for i in nearest_cells:
            if cells[i].resources <= 0:
                continue
            if target_type == 1 and cells[i].type != 1:
                continue
            if target_type == 2 and cells[i].type != 2:
                continue
            target = i
            b = {i}
            while parent[i] != i:
                i = parent[i]
                b.add(i)
            if sum(cells[i].opp_ants + 1 for i in beacons | b) > my_ants:
                break
            log(target, b)
            beacons |= b
        log(beacons)
        if beacons:
            output = ";".join(f"BEACON {b} 1" for b in beacons)
        else:
            output = "WAIT"
        output += f";MESSAGE ({my_ants}) vs ({opp_ants})"
        print(output)


if __name__ == '__main__':
    main()
