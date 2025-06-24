from enum import Enum

class Direction(Enum):
    R = 0 # Right
    L = 1 # Left
    D = 2 # Down
    U = 3 # Up
    RU = 4 # Right Up
    RD = 5 # Right Down
    LD = 6 # Left Down
    LU = 7 # Left Up
    H = 8 # HOLD

class It2s_Tiles_State:
    def __init__(self, quad: int, direction: Direction):
        self.quad = quad
        self.direction = direction


#  |-----------|-----------|-----------|-----------|-----------|
#  | Direction |   Quad0   |   Quad1   |   Quad2   |   Quad3   |
#  |===========|===========|===========|===========|===========|
#  |     R     |    1,H    |    0,R    |    3,H    |    2,R    |
#  |-----------|-----------|-----------|-----------|-----------|
#  |     L     |    1,L    |    0,H    |    3,L    |    2,H    |
#  |-----------|-----------|-----------|-----------|-----------|
#  |     D     |    2,H    |    3,H    |    0,D    |    1,D    |
#  |-----------|-----------|-----------|-----------|-----------|
#  |     U     |    2,U    |    3,U    |    0,H    |    1,H    |
#  |-----------|-----------|-----------|-----------|-----------|
#  |     RU    |    3,U    |    2,RU   |    1,H    |    0,R    |
#  |-----------|-----------|-----------|-----------|-----------|
#  |     RD    |    3,H    |    2,R    |    1,D    |    0,RD   |
#  |-----------|-----------|-----------|-----------|-----------|
#  |     LD    |    3,L    |    2,H    |    1,LD   |    0,D    |
#  |-----------|-----------|-----------|-----------|-----------|
#  |     LU    |    3,LU   |    2,U    |    1,L    |    0,H    |
#  |-----------|-----------|-----------|-----------|-----------|



QUAD_ADJACENTS_MATRIX = [
    [It2s_Tiles_State(1, Direction.H), It2s_Tiles_State(0, Direction.R), It2s_Tiles_State(3, Direction.H), It2s_Tiles_State(2, Direction.R)],
    [It2s_Tiles_State(1, Direction.L), It2s_Tiles_State(0, Direction.H), It2s_Tiles_State(3, Direction.L), It2s_Tiles_State(2, Direction.H)],
    [It2s_Tiles_State(2, Direction.H), It2s_Tiles_State(3, Direction.H), It2s_Tiles_State(0, Direction.D), It2s_Tiles_State(1, Direction.D)],
    [It2s_Tiles_State(2, Direction.U), It2s_Tiles_State(3, Direction.U), It2s_Tiles_State(0, Direction.H), It2s_Tiles_State(1, Direction.H)],
    [It2s_Tiles_State(3, Direction.U), It2s_Tiles_State(2, Direction.RU), It2s_Tiles_State(1, Direction.H), It2s_Tiles_State(0, Direction.R)],
    [It2s_Tiles_State(3, Direction.H), It2s_Tiles_State(2, Direction.R), It2s_Tiles_State(1, Direction.D), It2s_Tiles_State(0, Direction.RD)],
    [It2s_Tiles_State(3, Direction.L), It2s_Tiles_State(2, Direction.H), It2s_Tiles_State(1, Direction.LD), It2s_Tiles_State(0, Direction.D)],
    [It2s_Tiles_State(3, Direction.LU), It2s_Tiles_State(2, Direction.U), It2s_Tiles_State(1, Direction.L), It2s_Tiles_State(0, Direction.H)],
]

class It2s_Tiles:
    def __init__(self):
        self.convert = "0123"   # To convert quadrant later from int to string 

    def it2s_get_adjacent_tile(self, original_tile: str, direction: Direction) -> str:
        adjacent_tile = list(original_tile) # Convert string to list for mutability
        string_tracker = 1 # Start by the last quad
        next_state = It2s_Tiles_State(0, direction)
        while (next_state.direction != Direction.H):
            current_quad = int(original_tile[-string_tracker])
            next_state = QUAD_ADJACENTS_MATRIX[next_state.direction.value][current_quad]
            adjacent_tile[-string_tracker] = self.convert[next_state.quad]
            string_tracker += 2 # To skip a tile level back in case the search continues
        return "".join(adjacent_tile) # Convert list back to string

    def it2s_get_all_adjacent_tiles(self, original_tile: str) -> list:
        adjacent_tiles = []
        # TODO: Review in daemon, counting with the Hold too (original tile)
        for direction in Direction:
            adjacent_tiles.append(self.it2s_get_adjacent_tile(original_tile, direction))
        return adjacent_tiles   # String list of all adjacent tiles

if __name__ == "__main__":
    # https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8569941

    # Initialize the quadtree handler
    it2s = It2s_Tiles()

    # Test 1: Single tile adjacency in all directions
    print("Test 1: Single Tile Adjacency\n")
    original_tile = "/0/3/3/1/1/0/0/1/1/3/0/3/0/1"
    expected_results = {
        Direction.R: "/0/3/3/1/1/0/0/1/1/3/0/3/1/0",
        Direction.L: "/0/3/3/1/1/0/0/1/1/3/0/3/0/0",
        Direction.D: "/0/3/3/1/1/0/0/1/1/3/0/3/0/3",
        Direction.U: "/0/3/3/1/1/0/0/1/1/3/0/1/2/3",
        Direction.RU: "/0/3/3/1/1/0/0/1/1/3/0/1/3/2",
        Direction.RD: "/0/3/3/1/1/0/0/1/1/3/0/3/1/2",
        Direction.LD: "/0/3/3/1/1/0/0/1/1/3/0/3/0/2",
        Direction.LU: "/0/3/3/1/1/0/0/1/1/3/0/1/2/2",
        Direction.H: "/0/3/3/1/1/0/0/1/1/3/0/3/0/1",
    }

    for direction, expected_tile in expected_results.items():
        adj_tile = it2s.it2s_get_adjacent_tile(original_tile, direction)
        #print(f"Direction {direction.name}: {adj_tile} (Expected: {expected_tile})")
        assert adj_tile == expected_tile, f"Failed for direction {direction}"

    # Test 2: All tile adjacencies at once
    print("\nTest 2: All Tile Adjacencies\n")
    all_adjacent = it2s.it2s_get_all_adjacent_tiles(original_tile)
    expected_all_adjacent = [
        "/0/3/3/1/1/0/0/1/1/3/0/3/1/0",  # Right
        "/0/3/3/1/1/0/0/1/1/3/0/3/0/0",  # Left
        "/0/3/3/1/1/0/0/1/1/3/0/3/0/3",  # Down
        "/0/3/3/1/1/0/0/1/1/3/0/1/2/3",  # Up
        "/0/3/3/1/1/0/0/1/1/3/0/1/3/2",  # Right Up
        "/0/3/3/1/1/0/0/1/1/3/0/3/1/2",  # Right Down
        "/0/3/3/1/1/0/0/1/1/3/0/3/0/2",  # Left Down
        "/0/3/3/1/1/0/0/1/1/3/0/1/2/2",  # Left Up
    ]

    for result in expected_all_adjacent:
        assert result in all_adjacent, f"Failed for tile {result} not in {all_adjacent}"
        
    print("\nAll tests passed successfully!")