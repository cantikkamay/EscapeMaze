# ─── utils/enemy_ai.py ───────────────────────────────────────────────────────
# AI Satpam menggunakan BFS (Breadth-First Search) untuk pathfinding
# Sesuai GDD: Satpam mengejar pemain jika terdeteksi dalam range

from collections import deque


def bfs_path(grid, start, goal):
    """
    BFS dari start ke goal pada grid maze.
    grid[y][x] == 0 → bisa dilalui, == 1 → dinding.
    Kembalikan list koordinat (x,y) dari start ke goal,
    atau [] jika tidak ada jalur.
    """
    rows = len(grid)
    cols = len(grid[0])
    if not (0 <= start[0] < cols and 0 <= start[1] < rows):
        return []
    if not (0 <= goal[0] < cols and 0 <= goal[1] < rows):
        return []

    q = deque([start])
    visited = {start: None}

    while q:
        cx, cy = q.popleft()
        if (cx, cy) == goal:
            # Rekonstruksi jalur
            path = []
            node = goal
            while node is not None:
                path.append(node)
                node = visited[node]
            path.reverse()
            return path

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            if (0 <= nx < cols and 0 <= ny < rows
                    and grid[ny][nx] == 0
                    and (nx, ny) not in visited):
                visited[(nx, ny)] = (cx, cy)
                q.append((nx, ny))
    return []


def count_path_neighbors(grid, gx, gy):
    """
    Hitung berapa tile tetangga (4 arah) yang bisa dilalui.
    Digunakan untuk mendeteksi tile 'dead-end' (hanya 1 jalan keluar).
    """
    rows = len(grid)
    cols = len(grid[0])
    count = 0
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = gx + dx, gy + dy
        if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
            count += 1
    return count


def is_dead_end(grid, gx, gy):
    """
    Tile dianggap dead-end jika hanya punya 1 tetangga yang bisa dilalui.
    Bom TIDAK boleh diletakkan di sini agar pemain selalu punya jalan alternatif.
    """
    return count_path_neighbors(grid, gx, gy) <= 1


def is_on_critical_path(grid, gx, gy, start=(1, 1)):
    """
    Cek apakah tile (gx,gy) ada di jalur kritis menuju exit.
    Dianggap kritis jika menghapus tile ini memutus koneksi start→exit.
    Digunakan untuk menghindari bom di jalur wajib.
    """
    rows = len(grid)
    cols = len(grid[0])
    exit_pos = (cols - 2, rows - 2)

    # Buat grid sementara dengan tile ini dianggap dinding
    temp = [row[:] for row in grid]
    temp[gy][gx] = 1

    # Cek apakah masih ada jalur start → exit
    path = bfs_path(temp, start, exit_pos)
    return len(path) == 0   # True = kritis (memutus jalur)
