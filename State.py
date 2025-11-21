import json
import os

class CubeState:
    def __init__(self):
        self.solution = ""
        self.move_index = 0
        self.total_moves = 0
        self.expanded_moves_list = []
        self.state_file = "cube_state.json"
        self.load_state()
    
    def is_solved(self, cube_string):
        if len(cube_string) != 54:
            return False
        
        for i in range(6):
            face_start = i * 9
            face_end = face_start + 9
            face = cube_string[face_start:face_end]
            if len(set(face)) != 1:
                return False
        
        return True
    
    def set_solution(self, solution_str):
        self.solution = solution_str
        self.expanded_moves_list = self._expand_moves(solution_str)
        self.total_moves = len(self.expanded_moves_list)
        self.move_index = 0
    
    def _expand_moves(self, solution_str):
        expanded = []
        for move in solution_str.split():
            if move.endswith("2"):
                expanded.append(move)
            else:
                expanded.append(move)
        return expanded
    
    def expand_moves(self):
        return self.expanded_moves_list
    
    def count_moves(self):
        moves = self.solution.split()
        count = 0
        for move in moves:
            if move.endswith("2"):
                count += 2
            else:
                count += 1
        return count
    
    def next_move(self):
        if self.move_index < self.total_moves:
            self.move_index += 1
    
    def save_state(self):
        state_data = {
            "solution": self.solution,
            "move_index": self.move_index,
            "total_moves": self.total_moves,
            "expanded_moves": self.expanded_moves_list
        }
        with open(self.state_file, "w") as f:
            json.dump(state_data, f, indent=2)
    
    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    state_data = json.load(f)
                    self.solution = state_data.get("solution", "")
                    self.move_index = state_data.get("move_index", 0)
                    self.total_moves = state_data.get("total_moves", 0)
                    self.expanded_moves_list = state_data.get("expanded_moves", [])
            except:
                pass
    
    def reset_state(self):
        self.solution = ""
        self.move_index = 0
        self.total_moves = 0
        self.expanded_moves_list = []
        if os.path.exists(self.state_file):
            os.remove(self.state_file)