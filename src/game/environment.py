import random

class GameEnvironment:
    """
    Manages the game grid, towers, and core game mechanics.
    """
    
    def __init__(self, grid_size=18):
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
        
        # Track units that moved this turn (can't attack after moving)
        self.moved_units = set()
    
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
        
        # Mark the newly spawned unit as moved (can't attack on first turn)
        self.moved_units.add(unit_id)
        
        return unit_id
    
    def _is_valid_placement(self, position, player_id):
        """Check if a position is valid for placement."""
        # Check if position is within bounds and not occupied
        if position < 0 or position >= self.grid_size:
            return False
        
        if self.grid[position] != 0:
            return False
        
        # NEW RULE: Units can only be placed 1 or 2 blocks from their tower
        if player_id == 1:
            # Player 1's tower is at position 0
            # Valid positions are 1 and 2
            if position not in [1, 2]:
                return False
        else:  # player_id == 2
            # Player 2's tower is at position grid_size-1
            # Valid positions are grid_size-2 and grid_size-3
            if position not in [self.grid_size-2, self.grid_size-3]:
                return False
        
        return True
    
    def _process_movements(self):
        """Process all unit movements, including resolving stalemates."""
        # Increment turn counter at the start of movement phase
        self.turn_count += 1
        
        # Reset the moved units set at the beginning of each turn
        self.moved_units = set()
        
        # Check for stalemate situation (1-cell gap between opposing units)
        self._resolve_stalemates()
        
        # Sort units by their distance from the enemy tower
        # Player 1 units are sorted by descending position (furthest from enemy tower first)
        # Player 2 units are sorted by ascending position (furthest from enemy tower first)
        player1_units = [(unit_id, data) for unit_id, data in self.units.items() if data['owner'] == 1]
        player1_units.sort(key=lambda x: x[1]['position'], reverse=True)  # Furthest from enemy tower first
        
        player2_units = [(unit_id, data) for unit_id, data in self.units.items() if data['owner'] == 2]
        player2_units.sort(key=lambda x: x[1]['position'])  # Furthest from enemy tower first
        
        # Combine sorted units
        units_to_move = player1_units + player2_units
        
        for unit_id, unit_data in units_to_move:
            # Skip if unit was destroyed during this turn
            if unit_id not in self.units:
                continue
            
            position = unit_data['position']
            owner = unit_data['owner']
            
            # Determine movement direction based on owner
            # Player 1 units move right (increasing position)
            # Player 2 units move left (decreasing position)
            direction = 1 if owner == 1 else -1
            new_position = position + direction
            
            # Check if movement is possible
            if 0 <= new_position < self.grid_size and self.grid[new_position] == 0:
                # Update grid
                self.grid[position] = 0
                self.grid[new_position] = unit_id
                
                # Update unit data
                self.units[unit_id]['position'] = new_position
                
                # Mark the unit as moved (can't attack this turn)
                self.moved_units.add(unit_id)
    
    def _resolve_stalemates(self):
        """
        Resolve stalemate situations when there's a 1-cell gap between opposing units.
        The unit with higher HP will move into the gap.
        """
        # Find all empty cells
        empty_cells = [i for i, cell in enumerate(self.grid) if cell == 0]
        
        for empty_pos in empty_cells:
            # Check cells on both sides of the empty cell
            left_pos = empty_pos - 1
            right_pos = empty_pos + 1
            
            # Ensure positions are within grid bounds
            if left_pos < 0 or right_pos >= self.grid_size:
                continue
                
            left_cell = self.grid[left_pos]
            right_cell = self.grid[right_pos]
            
            # Skip if either cell isn't a unit
            if not isinstance(left_cell, int) or not isinstance(right_cell, int):
                continue
                
            # Skip if either unit doesn't exist anymore (might have been destroyed)
            if left_cell not in self.units or right_cell not in self.units:
                continue
                
            left_owner = self.units[left_cell]['owner']
            right_owner = self.units[right_cell]['owner']
            
            # Check if this is a stalemate between opposing units
            if left_owner != right_owner:
                # Get HP values for both units
                left_hp = self.units[left_cell]['card'].hp
                right_hp = self.units[right_cell]['card'].hp
                
                # The unit with higher HP moves into the gap
                if left_hp > right_hp:
                    # Move left unit (if it's Player 1)
                    if left_owner == 1:
                        self.grid[left_pos] = 0
                        self.grid[empty_pos] = left_cell
                        self.units[left_cell]['position'] = empty_pos
                        # Mark the unit as moved (can't attack this turn)
                        self.moved_units.add(left_cell)
                elif right_hp > left_hp:
                    # Move right unit (if it's Player 2)
                    if right_owner == 2:
                        self.grid[right_pos] = 0
                        self.grid[empty_pos] = right_cell
                        self.units[right_cell]['position'] = empty_pos
                        # Mark the unit as moved (can't attack this turn)
                        self.moved_units.add(right_cell)
                else:
                    # If HP values are equal, randomly choose which unit moves
                    # (This is a fallback for the rare case of equal HP)
                    if random.choice([True, False]):
                        # Move right unit (if it's Player 2)
                        if right_owner == 2:
                            self.grid[right_pos] = 0
                            self.grid[empty_pos] = right_cell
                            self.units[right_cell]['position'] = empty_pos
                            # Mark the unit as moved (can't attack this turn)
                            self.moved_units.add(right_cell)
                    else:
                        # Move left unit (if it's Player 1)
                        if left_owner == 1:
                            self.grid[left_pos] = 0
                            self.grid[empty_pos] = left_cell
                            self.units[left_cell]['position'] = empty_pos
                            # Mark the unit as moved (can't attack this turn)
                            self.moved_units.add(left_cell)
    
    def _process_attacks(self):
        """Process all attacks for units that haven't moved this turn."""
        # Make a copy of units to avoid modification during iteration
        units_copy = dict(self.units)
        
        for unit_id, unit_data in units_copy.items():
            # Skip units that moved this turn
            if unit_id in self.moved_units:
                continue
                
            position = unit_data['position']
            owner = unit_data['owner']
            card = unit_data['card']
            
            # Find targets within range
            targets = []
            for target_id, target_data in units_copy.items():
                # Skip if target is on the same team
                if target_data['owner'] == owner:
                    continue
                    
                target_pos = target_data['position']
                distance = abs(target_pos - position)
                
                # Check if target is within range
                if distance <= card.range:
                    targets.append((target_id, distance))
            
            # If no enemy units in range, check for tower
            if not targets:
                if owner == 1 and position + card.range >= self.grid_size - 1:
                    # Player 1's unit can attack Player 2's tower
                    self._attack_tower(unit_id, 2)
                elif owner == 2 and position - card.range <= 0:
                    # Player 2's unit can attack Player 1's tower
                    self._attack_tower(unit_id, 1)
                continue
            
            # Sort targets by distance (closest first)
            targets.sort(key=lambda x: x[1])
            
            # Attack the closest target
            self._attack_unit(unit_id, targets[0][0])

    def _attack_tower(self, attacker_id, tower_player):
        """Process an attack on a tower."""
        if attacker_id not in self.units:
            return
            
        attacker = self.units[attacker_id]['card']
        
        # Apply damage to tower
        if tower_player == 1:
            self.grid[0] = 'T1'  # Tower is destroyed
            self.game_over = True
            self.winner = 2
        else:
            self.grid[-1] = 'T2'  # Tower is destroyed
            self.game_over = True
            self.winner = 1

    def _attack_unit(self, attacker_id, defender_id):
        """Process an attack between two units."""
        # Verify both units still exist
        if attacker_id not in self.units or defender_id not in self.units:
            return
            
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
                'card_name': data['card'].name,
                'card_cost': data['card'].cost,
                'hp': data['card'].hp,
                'attack': data['card'].attack,
                'range': data['card'].range,
                'owner': data['owner'],
                'moved_this_turn': uid in self.moved_units
            } for uid, data in self.units.items()},
            'game_over': self.game_over,
            'winner': self.winner
        } 