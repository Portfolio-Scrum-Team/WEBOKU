class Climber:
    def __init__(self):
        self.current_ring = None
        self.current_column = None
        self.at_base = True
        self.at_roof = False
        self.movement_history = []

    @property
    def position(self):
        if self.at_base:
            return None
        return (self.current_ring, self.current_column)

    def move_to(self, ring, column):
        if not 1 <= ring <= 9:
            raise ValueError("Ring must be between 1 and 9")
        if not 1 <= column <= 9:
            raise ValueError("Column must be between 1 and 9")
        old_position = self.position
        self.current_ring = ring
        self.current_column = column
        self.at_base = False

        self.movement_history.append({"from": old_position, "to": self.position})

    def reset(self):
        self.current_ring = None
        self.current_column = None
        self.at_base = True
        self.at_roof = False
        self.movement_history = []

    def reach_princess(self):
        self.at_roof = True
        self.at_base = False

    def has_reached_princess(self):
        return self.at_roof
