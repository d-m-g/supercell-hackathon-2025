class Player:
    """
    Manages player state, including elixir and card deck.
    """
    
    def __init__(self, player_id, deck, max_elixir=10, initial_elixir=5):
        self.player_id = player_id
        self.deck = deck
        self.max_elixir = max_elixir
        self.elixir = initial_elixir
        self.hand = []  # Cards currently in hand
        self.next_card_index = 0
        
        # Initialize hand with 4 cards
        self._refill_hand()
    
    def _refill_hand(self):
        """Fill hand with cards from deck until hand has 4 cards or deck is empty."""
        while len(self.hand) < 4 and self.next_card_index < len(self.deck):
            self.hand.append(self.deck[self.next_card_index])
            self.next_card_index += 1
    
    def generate_elixir(self, amount=1):
        """Generate elixir for the player (called each turn)."""
        self.elixir = min(self.elixir + amount, self.max_elixir)
    
    def can_play_card(self, hand_index):
        """Check if the player can play a card from their hand."""
        if 0 <= hand_index < len(self.hand):
            return self.hand[hand_index].cost <= self.elixir
        return False
    
    def play_card(self, hand_index, position, game_env):
        """
        Play a card from the hand onto the game environment.
        
        Args:
            hand_index: Index of the card in the hand
            position: Position on the grid to place the card
            game_env: GameEnvironment instance
            
        Returns:
            unit_id if successful, None otherwise
        """
        if not self.can_play_card(hand_index):
            return None
        
        card = self.hand[hand_index]
        
        # Place the card on the grid
        unit_id = game_env.place_card(card, position, self.player_id)
        
        if unit_id:
            # Card placement was successful
            self.elixir -= card.cost
            self.hand.pop(hand_index)
            self._refill_hand()
            return unit_id
        
        return None
    
    def get_playable_cards(self):
        """Get a list of cards that can be played based on current elixir."""
        return [i for i, card in enumerate(self.hand) if card.cost <= self.elixir]
    
    def __str__(self):
        return f"Player {self.player_id} (Elixir: {self.elixir}/{self.max_elixir})"


class AIPlayer(Player):
    """
    AI-controlled player with basic decision-making for card placement.
    """
    
    def __init__(self, player_id, deck, max_elixir=10, initial_elixir=5, difficulty=1):
        super().__init__(player_id, deck, max_elixir, initial_elixir)
        self.difficulty = difficulty  # 1: Easy, 2: Medium, 3: Hard
    
    def make_move(self, game_env):
        """
        Decide which card to play and where to place it.
        
        Args:
            game_env: GameEnvironment instance
            
        Returns:
            True if a move was made, False otherwise
        """
        # Get playable cards
        playable_indices = self.get_playable_cards()
        
        if not playable_indices:
            return False
        
        # Simple AI: Always play the first playable card at a valid position
        import random
        
        # Sort playable cards by cost (higher difficulty prefers higher cost cards)
        if self.difficulty > 1:
            playable_indices.sort(
                key=lambda i: self.hand[i].cost,
                reverse=(self.difficulty == 3)  # Hard AI prefers expensive cards
            )
        else:
            # Easy AI randomizes card choice
            random.shuffle(playable_indices)
        
        # Try to play the selected card
        for hand_index in playable_indices:
            # Determine valid positions for this player
            if self.player_id == 1:
                # Player 1 starts on the left side
                valid_positions = list(range(1, game_env.grid_size // 2))
            else:
                # Player 2 starts on the right side
                valid_positions = list(range(game_env.grid_size // 2, game_env.grid_size - 1))
            
            # Shuffle positions for variety
            random.shuffle(valid_positions)
            
            for position in valid_positions:
                if game_env.grid[position] == 0:  # Position is empty
                    result = self.play_card(hand_index, position, game_env)
                    if result:
                        return True
                        
        return False 