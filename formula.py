import os
import json



def main():
    folder_path = "replays"
    replays = []

    troop_costs = {"knight": 3, "giant": 5, "goblin": 2, "archer": 3, "tower": 10}
    troop_max_hp = {"knight": 600, "giant": 1200, "goblin": 150, "archer": 250, "tower": 2000}


    # Check if the directory exists
    if not os.path.exists(folder_path):
        print(f"Error: {folder_path} directory does not exist")
        return
    # Iterate through all files in the replays folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Check if it's a file (not a directory) and has .json extension
        if os.path.isfile(file_path) and filename.lower().endswith('.json'):
            replays.append(file_path)
            # You can add your JSON processing logic here
    
    for replay in replays:
        with open(replay, 'r') as file:
            data = json.load(file)
            troopid_to_troop = {troop["troop_id"]: troop["troop_type"] for troop in data["troops_spawned"]}
            troop_performance = {
                "giant": 0,
                "knight": 0,
                "goblin": 0,
                "archer": 0
            }
            troop_count = {
                "giant": 0,
                "knight": 0,
                "goblin": 0,
                "archer": 0
            }
            for troop_id in troopid_to_troop:
                troop_type = troopid_to_troop[troop_id].lower()
                troop_count[troop_type] += 1
                troop_performance[troop_type] -= troop_costs[troop_type]
                for attack in data["attacks"]:
                    target, team = attack["target_type"].split("_")
                    target = target.lower()
                    team = team.lower()
                    if team == "player" and troop_id == attack["attacker_id"]:
                        troop_performance[troop_type] += (attack["damage"] / troop_max_hp[target]) * troop_costs[target] * 1.5
                    elif team == "player" and troop_id == attack["target_target_id"]:
                        troop_performance[troop_type] += (attack["damage"] / troop_max_hp[target]) * troop_costs[target] * 1

            for troop_type in troop_performance:
                if troop_count[troop_type] > 0:
                    troop_performance[troop_type] /= troop_count[troop_type]
                else:
                    troop_performance[troop_type] = 0
    
    print("Troop Performance:")
    for troop_type, performance in troop_performance.items():
        print(f"{troop_type}: {performance:.2f}")


if __name__ == "__main__":
    main()