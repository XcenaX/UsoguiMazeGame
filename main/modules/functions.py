from collections import deque
import uuid

def get_parameter(request, name):
    try:
        return request.GET[name]
    except:
        return None 

def post_parameter(request, name):
    try:
        return request.POST[name]
    except:
        return None 

def post_file(request, name):
    try:
        return request.FILES.getlist(name)
    except:
        return None

def session_parameter(request, name):
    try:
        return request.session[name]
    except:
        return None
    
def get_current_user(request):
    if request.user.is_authenticated:
        return request.user, True
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key, False


def is_path_available(entrance, exit, walls, board_size=6):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def can_move(from_x, from_y, to_x, to_y):
        if 0 <= to_x < board_size and 0 <= to_y < board_size:
            if [from_x, from_y, to_x, to_y] in walls or [to_x, to_y, from_x, from_y] in walls:
                return False
            return True
        return False

    # BFS
    queue = deque([entrance])
    visited = set()
    visited.add((entrance['x'], entrance['y']))

    while queue:
        current = queue.popleft()
        x, y = current['x'], current['y']
        
        if (x, y) == (exit['x'], exit['y']):
            return True  # Путь найден

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if can_move(x, y, nx, ny) and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append({'x': nx, 'y': ny})
                
    return False


def can_move_to(current_position, wanted_position, walls):
    x1, y1 = current_position['x'], current_position['y']
    x2, y2 = wanted_position['x'], wanted_position['y']
    if abs(x1 - x2) + abs(y1 - y2) != 1:
        raise Exception("Invalid move")
    if [x1, y1, x2, y2] in walls or [x2, y2, x1, y1] in walls:
        return False  # Ход невозможен, есть стена
    return True

def update_spotted_walls(current_position, wanted_position, spotted_walls):
    x1, y1 = current_position['x'], current_position['y']
    x2, y2 = wanted_position['x'], wanted_position['y']
    if [x1, y1, x2, y2] not in spotted_walls and [x2, y2, x1, y1] not in spotted_walls:
        spotted_walls.append([x1, y1, x2, y2])
    return spotted_walls

def get_available_moves(current_position, walls):
    x, y = current_position['x'], current_position['y']
    possible_moves = [
        {"x": x+1, "y": y},
        {"x": x-1, "y": y},
        {"x": x, "y": y+1},
        {"x": x, "y": y-1}
    ]
    available_moves = []
    for move in possible_moves:
        try:
            if can_move_to(current_position, move, walls):
                available_moves.append(move)            
        except:
            return []
    return available_moves
