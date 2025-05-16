class GameEnvironment:
    """
    Manages the game grid, towers, and core game mechanics.
    """
    
    def __init__(self, grid_size=10):
        # Initialize the grid with zeros (empty spaces)
        self.grid_size = grid_size
        self.grid = [0] * grid_size
        
        # Place towers at each end
        self.grid[0] = 'T1'  # Player 1's tower
        self.grid[-1] = 'T2'  # Player 2's tower
        
        # Game state
        self.turn_count = 0
        self.game_over = False
        self.winner = None
        
        # Units on the field (id: {position, card_instance, owner})
        self.units = {}
        self.next_unit_id = 1
    
    def place_card(self, card, position, player_id):
        """Place a card on the grid."""
        if not self._is_valid_placement(position, player_id):
            return False
        
        # Create a new unit and place it on the grid
        unit_id = self.next_unit_id
        self.next_unit_id += 1
        
        self.units[unit_id] = {
            'position': position,
            'card': card.copy(),  # Create a copy of the card
            'owner': player_id
        }
        
        self.grid[position] = unit_id
        return unit_id
    
    def _is_valid_placement(self, position, player_id):
        """Check if a position is valid for placement."""
        # Check if position is within bounds and not occupied
        if position < 0 or position >= self.grid_size:
            return False
        
        if self.grid[position] != 0:
            return False
        
        # Player 1 can only place cards on their half (left side)
        if player_id == 1 and position > self.grid_size // 2:
            return False
        
        # Player 2 can only place cards on their half (right side)
        if player_id == 2 and position < self.grid_size // 2:
            return False
        
        return True
    
    def process_turn(self):
        """Process a single turn of the game."""
        self.turn_count += 1
        
        # Process all units movement and attacks
        self._process_movements()
        self._process_attacks()
        
        # Check win conditions
        self._check_win_conditions()
        
        # Return the current state
        return self._get_state()
    
    def _process_movements(self):
        """Move all units according to their movement rules."""
        # Sort units by position to prevent movement conflicts
        units_to_move = sorted(
            [(unit_id, data) for unit_id, data in self.units.items()],
            key=lambda x: x[1]['position']
        )
        
        for unit_id, unit_data in units_to_move:
            # Skip if unit was destroyed during this turn
            if unit_id not in self.units:
                continue
            
            position = unit_data['position']
            owner = unit_data['owner']
            
            # Determine movement direction based on owner
            direction = 1 if owner == 1 else -1
            new_position = position + direction
            
            # Check if movement is possible
            if 0 <= new_position < self.grid_size and self.grid[new_position] == 0:
                # Update grid
                self.grid[position] = 0
                self.grid[new_position] = unit_id
                
                # Update unit data
                self.units[unit_id]['position'] = new_position
    
    def _process_attacks(self):
        """Process attacks for all units."""
        for unit_id, unit_data in list(self.units.items()):
            position = unit_data['position']
            owner = unit_data['owner']
            card = unit_data['card']
            
            # Determine attack direction and target position
            direction = 1 if owner == 1 else -1
            target_position = position + direction
            
            # Check if target is within bounds
            if 0 <= target_position < self.grid_size:
                target = self.grid[target_position]
                
                # Check if target is a unit or tower
                if target != 0:
                    if target == 'T1' and owner == 2:
                        # Player 2 wins if they damage player 1's tower
                        self.game_over = True
                        self.winner = 2
                    elif target == 'T2' and owner == 1:
                        # Player 1 wins if they damage player 2's tower
                        self.game_over = True
                        self.winner = 1
                    elif isinstance(target, int):  # Target is a unit
                        self._attack_unit(unit_id, target)
    
    def _attack_unit(self, attacker_id, defender_id):
        """Process an attack between two units."""
        attacker = self.units[attacker_id]['card']
        defender = self.units[defender_id]['card']
        
        # Apply damage
        defender.hp -= attacker.attack
        
        # Check if defender is destroyed
        if defender.hp <= 0:
            # Remove defender from the grid and units list
            position = self.units[defender_id]['position']
            self.grid[position] = 0
            del self.units[defender_id]
    
    def _check_win_conditions(self):
        """Check if any player has won."""
        # Win conditions already checked during attacks
        pass
    
    def _get_state(self):
        """Return the current game state for replay and analysis."""
        return {
            'turn': self.turn_count,
            'grid': self.grid.copy(),
            'units': {uid: {
                'position': data['position'],
                'hp': data['card'].hp,
                'attack': data['card'].attack,
                'owner': data['owner']
            } for uid, data in self.units.items()},
            'game_over': self.game_over,
            'winner': self.winner
        } 