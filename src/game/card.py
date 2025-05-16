class Card:
    """
    Represents a character card with attributes and behavior.
    """
    
    def __init__(self, name, attack, hp, cost):
        self.name = name
        self.attack = attack
        self.hp = hp
        self.cost = cost
        self.original_hp = hp  # Store original HP for reference
    
    def copy(self):
        """Create a copy of this card."""
        return Card(self.name, self.attack, self.hp, self.cost)
    
    def is_alive(self):
        """Check if the card is still alive."""
        return self.hp > 0
    
    def reset(self):
        """Reset the card to its original state."""
        self.hp = self.original_hp
        
    def __str__(self):
        return f"{self.name} (ATK:{self.attack}, HP:{self.hp}, Cost:{self.cost})"
    
    def __repr__(self):
        return f"Card({self.name}, {self.attack}, {self.hp}, {self.cost})"


class CardDeck:
    """
    Manages a collection of cards for a player.
    """
    
    def __init__(self, cards=None):
        self.cards = cards or []
    
    def add_card(self, card):
        """Add a card to the deck."""
        self.cards.append(card)
    
    def remove_card(self, index):
        """Remove a card from the deck by index."""
        if 0 <= index < len(self.cards):
            return self.cards.pop(index)
        return None
    
    def get_card(self, index):
        """Get a card from the deck without removing it."""
        if 0 <= index < len(self.cards):
            return self.cards[index]
        return None
    
    def shuffle(self):
        """Shuffle the deck."""
        import random
        random.shuffle(self.cards)
    
    def __len__(self):
        return len(self.cards)
    
    def __getitem__(self, index):
        return self.cards[index]
    
    def __iter__(self):
        return iter(self.cards)


# Define some sample cards
def create_sample_cards():
    """Create a set of sample cards for testing."""
    return [
        Card("Knight", attack=5, hp=10, cost=3),
        Card("Archer", attack=4, hp=4, cost=2),
        Card("Giant", attack=10, hp=20, cost=5),
        Card("Goblin", attack=3, hp=3, cost=1),
        Card("Wizard", attack=4, hp=5, cost=4),
        Card("Skeleton", attack=2, hp=1, cost=1),
    ] 