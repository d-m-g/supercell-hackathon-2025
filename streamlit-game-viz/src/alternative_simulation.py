import pygame
import random
import json
import os
from datetime import datetime
import time
import sys

# Check if running in Streamlit Cloud environment
is_streamlit_cloud = os.environ.get('STREAMLIT_RUNTIME_ENV') == 'cloud'

# Only import pyautogui if we're in a local environment with a display
try:
    if not is_streamlit_cloud:
        import pyautogui
except ImportError:
    print("PyAutoGUI not available or display not detected")

# Initialize Pygame in headless mode for Streamlit - set these BEFORE pygame.init()
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame welcome message

# Initialize pygame with minimal display
try:
    # Disable actual window creation
    pygame.display.set_mode = lambda *args, **kwargs: pygame.Surface((800, 600))
    # Initialize pygame without window
    pygame.init()
except Exception as e:
    print(f"Pygame initialization error: {e}")

# Simulation settings
AUTO_RESTART = True  # Automatically save replays

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LANE_WIDTH = 120
GAME_SPEED = 10.0  # Simulation speed multiplier
TICK_RATE = 60  # Game logic ticks per second
FPS = 60 * GAME_SPEED  # Frames per second for rendering
TOWER_DAMAGE = 30  # Default 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Player constants
PLAYER_ELIXIR_MAX = 10
ELIXIR_REGEN_RATE = 0.35  # Elixir per second

# Tower positions
PLAYER_TOWER_POS = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
ENEMY_TOWER_POS = (SCREEN_WIDTH // 2, 50)

# Create a surface for rendering (no actual window will be created in headless mode)
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create a clock for timing
clock = pygame.time.Clock()

# Font setup
try:
    font = pygame.font.SysFont('Arial', 18)
except Exception as e:
    print(f"Font initialization error: {e}")
    # Fallback if font fails
    font = pygame.font.Font(None, 18)

class Tower:
    def __init__(self, position, hp, team, attack_damage=TOWER_DAMAGE, attack_speed=1.5, attack_range=200):
        self.position = position
        self.max_hp = hp
        self.hp = hp
        self.team = team  # 'player' or 'enemy'
        self.attack_damage = attack_damage
        self.attack_speed = attack_speed  # Attacks per second
        self.attack_range = attack_range
        self.attack_cooldown = 0
        self.width = 80
        self.height = 80
        self.target = None
        self.last_attack_tick = 0

    def draw(self):
        # Draw tower body
        tower_color = BLUE if self.team == 'player' else RED
        rect = pygame.Rect(
            self.position[0] - self.width // 2,
            self.position[1] - self.height // 2,
            self.width,
            self.height
        )
        pygame.draw.rect(screen, tower_color, rect)
        
        # Draw health bar
        health_ratio = self.hp / self.max_hp
        health_bar_width = self.width
        health_bar_height = 10
        health_bar_rect = pygame.Rect(
            self.position[0] - health_bar_width // 2,
            self.position[1] - self.height // 2 - 15,
            health_bar_width,
            health_bar_height
        )
        pygame.draw.rect(screen, BLACK, health_bar_rect, 1)
        pygame.draw.rect(screen, GREEN, (
            health_bar_rect.left + 1,
            health_bar_rect.top + 1,
            (health_bar_width - 2) * health_ratio,
            health_bar_height - 2
        ))
        
        # Draw tower health text
        hp_text = font.render(f"HP: {int(self.hp)}", True, BLACK)
        hp_text_rect = hp_text.get_rect(center=(self.position[0], self.position[1]))
        screen.blit(hp_text, hp_text_rect)

    def update(self, troops, current_tick):
        # Attack cooldown
        ticks_since_last_attack = current_tick - self.last_attack_tick
        cooldown_ticks = TICK_RATE / (self.attack_speed * GAME_SPEED)
        if ticks_since_last_attack < cooldown_ticks:
            return None  # Still on cooldown
        
        # Find target
        closest_troop = None
        closest_distance = float('inf')
        
        for troop in troops:
            if troop.team != self.team:  # Only target enemies
                distance = ((self.position[0] - troop.position[0]) ** 2 + 
                           (self.position[1] - troop.position[1]) ** 2) ** 0.5
                if distance <= self.attack_range and distance < closest_distance:
                    closest_troop = troop
                    closest_distance = distance
        
        # Attack if target found
        if closest_troop:
            self.target = closest_troop
            self.last_attack_tick = current_tick
            closest_troop.take_damage(self.attack_damage)
            
            # Get the target's current target
            target_target_id = None
            target_target_type = None
            if closest_troop.target:
                target_target_id = id(closest_troop.target)
                if hasattr(closest_troop.target, 'troop_type'):
                    target_target_type = f"{closest_troop.target.troop_type}_{closest_troop.target.team}"
                else:
                    target_target_type = f"Tower_ {closest_troop.target.team}"
            
            # Return attack data for replay
            return {
                "tick": current_tick,
                "attacker_id": id(self),
                "attacker_type": f"Tower_{self.team}",
                "target_id": id(closest_troop),
                "target_type": f"{closest_troop.troop_type}_{closest_troop.team}",
                "damage": self.attack_damage,
                "target_target_id": target_target_id,
                "target_target_type": target_target_type
            }
        
        return None


class Troop:
    def __init__(self, position, troop_type, team, cost, lane_position=SCREEN_WIDTH // 2):
        self.position = list(position)
        self.troop_type = troop_type
        self.team = team  # 'player' or 'enemy'
        self.cost = cost
        self.lane_position = lane_position  # X position in lane
        
        # Default stats
        self.hp = 100
        self.max_hp = 100
        self.attack_damage = 30
        self.attack_speed = 1.0  # Attacks per second
        self.move_speed = 50  # Pixels per second
        self.attack_range = 50
        self.size = 30
        self.target = None
        self.last_attack_tick = 0
        
        # Set specific stats based on troop type
        self.set_troop_stats()

    def set_troop_stats(self):
        if self.troop_type == "Knight":
            self.hp = 600
            self.max_hp = 600
            self.attack_damage = 80
            self.attack_speed = 1.2
            self.move_speed = 40
            self.attack_range = 60
            self.size = 35
        elif self.troop_type == "Archer":
            self.hp = 250
            self.max_hp = 250
            self.attack_damage = 50
            self.attack_speed = 1.8
            self.move_speed = 60
            self.attack_range = 200
            self.size = 30
        elif self.troop_type == "Giant":
            self.hp = 1200
            self.max_hp = 1200
            self.attack_damage = 120
            self.attack_speed = 0.8
            self.move_speed = 30
            self.attack_range = 70
            self.size = 45
        elif self.troop_type == "Goblin":
            self.hp = 150
            self.max_hp = 150
            self.attack_damage = 35
            self.attack_speed = 2.0
            self.move_speed = 80
            self.attack_range = 40
            self.size = 25

    def draw(self):
        troop_color = BLUE if self.team == 'player' else RED
        
        # Draw troop body
        pygame.draw.circle(screen, troop_color, (int(self.position[0]), int(self.position[1])), self.size)
        
        # Draw troop type text
        text = font.render(self.troop_type, True, BLACK)
        text_rect = text.get_rect(center=(int(self.position[0]), int(self.position[1]) - self.size - 10))
        screen.blit(text, text_rect)
        
        # Draw health bar
        health_ratio = self.hp / self.max_hp
        health_bar_width = self.size * 2
        health_bar_height = 5
        health_bar_rect = pygame.Rect(
            int(self.position[0]) - health_bar_width // 2,
            int(self.position[1]) - self.size - 5,
            health_bar_width,
            health_bar_height
        )
        pygame.draw.rect(screen, BLACK, health_bar_rect, 1)
        pygame.draw.rect(screen, GREEN, (
            health_bar_rect.left + 1,
            health_bar_rect.top + 1,
            (health_bar_width - 2) * health_ratio,
            health_bar_height - 2
        ))

    def move(self, dt, troops, towers):
        # Scale dt by GAME_SPEED
        scaled_dt = dt * GAME_SPEED
        
        # Check if there are enemies within attack range
        in_combat = False
        
        # First check enemy troops
        for troop in troops:
            if troop.team != self.team:
                distance = ((self.position[0] - troop.position[0]) ** 2 + 
                        (self.position[1] - troop.position[1]) ** 2) ** 0.5
                if distance <= self.attack_range:
                    in_combat = True
                    break
        
        if self.troop_type == "Giant":
            in_combat = False  # Giants do not attack other troops

        # Then check enemy towers if not already in combat
        if not in_combat:
            for tower in towers:
                if tower.team != self.team:
                    distance = ((self.position[0] - tower.position[0]) ** 2 + 
                            (self.position[1] - tower.position[1]) ** 2) ** 0.5
                    if distance <= self.attack_range:
                        in_combat = True
                        break
        
        # If not in combat, move towards enemy tower
        if not in_combat:
            move_direction = -1 if self.team == 'player' else 1
            self.position[1] += move_direction * self.move_speed * scaled_dt
            
            # Keep troop in the lane
            self.position[0] = self.lane_position

    def update(self, dt, troops, towers, current_tick):
        self.move(dt, troops, towers)
        return self.attack(troops, towers, current_tick)

    def attack(self, troops, towers, current_tick):
        # Attack cooldown
        ticks_since_last_attack = current_tick - self.last_attack_tick
        cooldown_ticks = TICK_RATE / (self.attack_speed * GAME_SPEED)
        if ticks_since_last_attack < cooldown_ticks:
            return None  # Still on cooldown
        
        # First priority: enemy troops in range
        closest_enemy = None
        closest_distance = float('inf')
        
        for troop in troops:
            if troop.team != self.team:
                distance = ((self.position[0] - troop.position[0]) ** 2 + 
                           (self.position[1] - troop.position[1]) ** 2) ** 0.5
                if distance <= self.attack_range and distance < closest_distance:
                    closest_enemy = troop
                    closest_distance = distance
        
        # If no troops in range, check for towers
        if not closest_enemy:
            for tower in towers:
                if tower.team != self.team:
                    distance = ((self.position[0] - tower.position[0]) ** 2 + 
                               (self.position[1] - tower.position[1]) ** 2) ** 0.5
                    if distance <= self.attack_range:
                        # Attack tower
                        self.target = tower
                        self.last_attack_tick = current_tick
                        tower.hp -= self.attack_damage
                        
                        # Tower's target information (could be None)
                        target_target_id = None
                        target_target_type = None
                        if tower.target:
                            target_target_id = id(tower.target)
                            target_target_type = f"{tower.target.troop_type}_{tower.target.team}"
                        
                        # Return attack data for replay
                        return {
                            "tick": current_tick,
                            "attacker_id": id(self),
                            "attacker_type": f"{self.troop_type}_{self.team}",
                            "target_id": id(tower),
                            "target_type": f"{tower.team}_tower",
                            "damage": self.attack_damage,
                            "target_target_id": target_target_id,
                            "target_target_type": target_target_type
                        }
        
        # If found enemy troop, attack it
        if closest_enemy:
            self.target = closest_enemy
            self.last_attack_tick = current_tick
            closest_enemy.take_damage(self.attack_damage)
            
            # Get the target's current target
            target_target_id = None
            target_target_type = None
            if closest_enemy.target:
                target_target_id = id(closest_enemy.target)
                if hasattr(closest_enemy.target, 'troop_type'):
                    target_target_type = f"{closest_enemy.target.troop_type}_{closest_enemy.target.team}"
                else:
                    target_target_type = f"{closest_enemy.target.team}_tower"
            
            # Return attack data for replay
            return {
                "tick": current_tick,
                "attacker_id": id(self),
                "attacker_type": f"{self.troop_type}_{self.team}",
                "target_id": id(closest_enemy),
                "target_type": f"{closest_enemy.troop_type}_{closest_enemy.team}",
                "damage": self.attack_damage,
                "target_target_id": target_target_id,
                "target_target_type": target_target_type
            }
        
        return None

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def is_dead(self):
        return self.hp <= 0


class Player:
    def __init__(self, is_ai=False):
        self.elixir = 5
        self.deck = ["Knight", "Archer", "Giant", "Goblin"]
        self.is_ai = is_ai
        self.ai_deploy_timer = 0
        self.next_troop = None

    def update(self, dt):
        # Scale dt by GAME_SPEED
        scaled_dt = dt * GAME_SPEED
        # Regenerate elixir
        if self.elixir < PLAYER_ELIXIR_MAX:
            self.elixir += ELIXIR_REGEN_RATE * scaled_dt
            if self.elixir > PLAYER_ELIXIR_MAX:
                self.elixir = PLAYER_ELIXIR_MAX

    def deploy_troop(self, troop_type, team, lane_position):
        # Define troop costs
        troop_costs = {
            "Knight": 3,
            "Archer": 2,
            "Giant": 5,
            "Goblin": 1
        }
        
        cost = troop_costs.get(troop_type, 2)
        
        if self.elixir >= cost:
            position = [lane_position, SCREEN_HEIGHT - 150] if team == 'player' else [lane_position, 150]
            troop = Troop(position, troop_type, team, cost, lane_position)
            self.elixir -= cost
            return troop
        return None

    def ai_update(self, dt, game_state):
        # Scale dt by GAME_SPEED
        scaled_dt = dt * GAME_SPEED
        self.ai_deploy_timer += scaled_dt
        
        # Scale the deployment time based on GAME_SPEED
        deploy_time = random.uniform(3, 6) / GAME_SPEED
        if self.ai_deploy_timer >= deploy_time:
            self.ai_deploy_timer = 0
            
            if not self.next_troop:
                self.next_troop = random.choice(self.deck)
            troop_type = self.next_troop

            if self.elixir >= game_state.get_troop_cost(troop_type):
                
                # Deploy in the middle of the lane with small random offset
                lane_position = SCREEN_WIDTH // 2 + random.randint(-20, 20)
                self.next_troop = None  # Reset next troop after deploying
                return self.deploy_troop(troop_type, 'enemy', lane_position)
        
        return None


class GameState:
    def __init__(self):
        self.player = Player(is_ai=True)
        self.enemy = Player(is_ai=True)
        self.troops = []
        self.player_tower = Tower(PLAYER_TOWER_POS, 2000, 'player')
        self.enemy_tower = Tower(ENEMY_TOWER_POS, 2000, 'enemy')
        self.towers = [self.player_tower, self.enemy_tower]
        self.selected_troop = "Knight"
        self.game_over = False
        self.winner = None
        self.current_tick = 0
        
        # Replay data
        self.replay_data = {
            "game_start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "troops_spawned": [],
            "attacks": [],
            "troop_deaths": [],
            "game_result": None
        }

    def update(self, dt):
        if self.game_over:
            return

        scaled_dt = dt * GAME_SPEED

        self.current_tick += 1
        
        # Update players
        self.player.update(scaled_dt)
        self.enemy.update(scaled_dt)
        
        # AI opponent logic
        ai_troop = self.enemy.ai_update(scaled_dt, self)
        if ai_troop:
            self.troops.append(ai_troop)
            self.replay_data["troops_spawned"].append({
            "tick": self.current_tick,
            "troop_id": id(ai_troop),
            "troop_type": ai_troop.troop_type,
            "team": ai_troop.team,
            "position": ai_troop.position.copy()
            })
            
        # AI player logic
        if self.player.is_ai:
            player_ai_troop = self.player.ai_update(scaled_dt, self)
            if player_ai_troop:
            # For player AI, troops should be deployed at the bottom
                player_ai_troop.position = [player_ai_troop.lane_position, SCREEN_HEIGHT - 150]
                player_ai_troop.team = 'player'  # Ensure the team is set correctly
                self.troops.append(player_ai_troop)
                self.replay_data["troops_spawned"].append({
                    "tick": self.current_tick,
                    "troop_id": id(player_ai_troop),
                    "troop_type": player_ai_troop.troop_type,
                    "team": player_ai_troop.team,
                    "position": player_ai_troop.position.copy()
                })
        
        # Update troops and record attacks
        dead_troops = []
        for troop in self.troops:
            attack_data = troop.update(scaled_dt, self.troops, self.towers, self.current_tick)
            if attack_data:
                self.replay_data["attacks"].append(attack_data)
            
            if troop.is_dead():
                dead_troops.append(troop)
                self.replay_data["troop_deaths"].append({
                    "tick": self.current_tick,
                    "troop_id": id(troop),
                    "troop_type": troop.troop_type,
                    "team": troop.team
                })
        
        # Remove dead troops
        for troop in dead_troops:
            self.troops.remove(troop)
        
        # Update towers and record attacks
        for tower in self.towers:
            attack_data = tower.update(self.troops, self.current_tick)
            if attack_data:
                self.replay_data["attacks"].append(attack_data)
        
        # Check win conditions
        if self.player_tower.hp <= 0:
            self.game_over = True
            self.winner = 'enemy'
            self.replay_data["game_result"] = {"winner": "enemy", "end_tick": self.current_tick}
        elif self.enemy_tower.hp <= 0:
            self.game_over = True
            self.winner = 'player'
            self.replay_data["game_result"] = {"winner": "player", "end_tick": self.current_tick}

    def draw(self):
        # Clear screen
        screen.fill(WHITE)
        
        # Draw lane
        lane_rect = pygame.Rect(
            (SCREEN_WIDTH - LANE_WIDTH) // 2,
            0,
            LANE_WIDTH,
            SCREEN_HEIGHT
        )
        pygame.draw.rect(screen, GRAY, lane_rect)
        
        # Draw towers
        for tower in self.towers:
            tower.draw()
        
        # Draw troops
        for troop in self.troops:
            troop.draw()
        
        # Draw elixir bar
        elixir_bar_width = 200
        elixir_bar_height = 20
        elixir_bar_rect = pygame.Rect(
            20,
            SCREEN_HEIGHT - 30,
            elixir_bar_width,
            elixir_bar_height
        )
        pygame.draw.rect(screen, BLACK, elixir_bar_rect, 1)
        pygame.draw.rect(screen, (128, 0, 128), (
            elixir_bar_rect.left + 1,
            elixir_bar_rect.top + 1,
            (elixir_bar_width - 2) * (self.player.elixir / PLAYER_ELIXIR_MAX),
            elixir_bar_height - 2
        ))
        
        # Draw elixir text
        elixir_text = font.render(f"Elixir: {int(self.player.elixir)}/{PLAYER_ELIXIR_MAX}", True, BLACK)
        screen.blit(elixir_text, (30, SCREEN_HEIGHT - 50))
        
        # Draw currently selected troop
        selected_text = font.render(f"Selected: {self.selected_troop}", True, BLACK)
        screen.blit(selected_text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50))
        
        # Draw troop deck
        deck_x = SCREEN_WIDTH - 300
        deck_y = SCREEN_HEIGHT - 80
        for i, troop_type in enumerate(self.player.deck):
            troop_cost = self.get_troop_cost(troop_type)
            troop_rect = pygame.Rect(deck_x + i * 70, deck_y, 60, 60)
            
            # Highlight selected troop
            if troop_type == self.selected_troop:
                pygame.draw.rect(screen, (200, 200, 255), troop_rect)
            else:
                pygame.draw.rect(screen, WHITE, troop_rect)
            
            pygame.draw.rect(screen, BLACK, troop_rect, 2)
            
            # Draw troop name and cost
            troop_name_text = font.render(troop_type, True, BLACK)
            troop_cost_text = font.render(f"{troop_cost}", True, (128, 0, 128))
            
            screen.blit(troop_name_text, (deck_x + i * 70 + 5, deck_y + 10))
            screen.blit(troop_cost_text, (deck_x + i * 70 + 25, deck_y + 35))
        
        # Draw game over message if applicable
        if self.game_over:
            font_large = pygame.font.SysFont('Arial', 48)
            if self.winner == 'player':
                text = font_large.render("YOU WIN!", True, BLUE)
            else:
                text = font_large.render("YOU LOSE!", True, RED)
            
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text, text_rect)
            
            # Draw restart message
            restart_text = font.render("Press R to restart", True, BLACK)
            restart_text_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(restart_text, restart_text_rect)
            
        
        # Update display
        pygame.display.flip()

    def get_troop_cost(self, troop_type):
        # Define troop costs
        troop_costs = {
            "Knight": 3,
            "Archer": 2,
            "Giant": 5,
            "Goblin": 1
        }
        return troop_costs.get(troop_type, 2)

    def save_replay(self):
        # Save to the replays directory at the project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        replay_dir = os.path.join(project_root, "replays")
        if not os.path.exists(replay_dir):
            os.makedirs(replay_dir)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(replay_dir, f"clash_replay_{timestamp}.json")
        
        # Save replay data to JSON file
        with open(filename, 'w') as f:
            json.dump(self.replay_data, f, indent=2)
        
        print(f"Replay saved to {filename}")
        return filename


def replay_viewer(replay_file):
    """
    Function to view a saved replay file
    """
    # Load replay data
    with open(replay_file, 'r') as f:
        replay_data = json.load(f)
    
    print(f"Loaded replay from {replay_data['game_start_time']}")
    print(f"Game result: {replay_data['game_result']['winner']} won at tick {replay_data['game_result']['end_tick']}")
    print(f"Total troops spawned: {len(replay_data['troops_spawned'])}")
    print(f"Total attacks recorded: {len(replay_data['attacks'])}")
    
    # Print troop spawn events
    print("\nTroop Spawn Events:")
    for spawn in replay_data['troops_spawned']:
        print(f"Tick {spawn['tick']}: {spawn['team']} {spawn['troop_type']} spawned at {spawn['position']}")
    
    # Print attack events (first 10)
    print("\nAttack Events (first 10):")
    for i, attack in enumerate(replay_data['attacks'][:10]):
        target_targeting_info = ""
        if attack.get('target_target_type'):
            target_targeting_info = f" (targeting: {attack['target_target_type']})"
        print(f"Tick {attack['tick']}: {attack['attacker_type']} attacked {attack['target_type']}{target_targeting_info} for {attack['damage']} damage")
    
    # Print death events
    print("\nTroop Death Events:")
    for death in replay_data['troop_deaths']:
        print(f"Tick {death['tick']}: {death['team']} {death['troop_type']} died")


def main(n=1):
    game_state = GameState()
    running = True
    
    # Main game loop
    while running:
        dt = clock.tick(FPS) / 1000.0  # Time passed in seconds
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_state.game_over:
                    # Save replay before restarting
                    game_state.save_replay()
                    game_state = GameState()
                
                # Troop selection keys
                if event.key == pygame.K_1:
                    game_state.selected_troop = "Knight"
                elif event.key == pygame.K_2:
                    game_state.selected_troop = "Archer"
                elif event.key == pygame.K_3:
                    game_state.selected_troop = "Giant"
                elif event.key == pygame.K_4:
                    game_state.selected_troop = "Goblin"
                
                # Save replay manually with S key
                if event.key == pygame.K_s:
                    game_state.save_replay()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Deploy troop if clicked in lane
                    mouse_pos = pygame.mouse.get_pos()
                    lane_left = (SCREEN_WIDTH - LANE_WIDTH) // 2
                    lane_right = lane_left + LANE_WIDTH
                    
                    if (lane_left <= mouse_pos[0] <= lane_right and 
                        mouse_pos[1] > SCREEN_HEIGHT // 2):
                        
                        # Deploy troop at clicked position
                        troop = game_state.player.deploy_troop(
                            game_state.selected_troop, 
                            'player',
                            mouse_pos[0]
                        )
                        
                        if troop:
                            game_state.troops.append(troop)
                            game_state.replay_data["troops_spawned"].append({
                                "tick": game_state.current_tick,
                                "troop_id": id(troop),
                                "troop_type": troop.troop_type,
                                "team": troop.team,
                                "position": troop.position.copy()
                            })
        
        # Update game
        game_state.update(dt)
        
        # Draw everything
        game_state.draw()
    
    # Save replay before quitting
    if game_state.game_over:
        game_state.save_replay()
    
    pygame.quit()


if __name__ == "__main__":
    main() 