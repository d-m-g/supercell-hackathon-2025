import os
import json
import sys


def analyze_replay(replay_path):
    """Analyze a single replay file and return troop performance metrics"""
    troop_costs = {"knight": 3, "giant": 5, "goblin": 2, "archer": 3, "tower": 10}
    troop_max_hp = {"knight": 600, "giant": 1200, "goblin": 150, "archer": 250, "tower": 2000}
    
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
    
    try:
        with open(replay_path, 'r') as file:
            data = json.load(file)
            
            # Map troop IDs to troop types
            troopid_to_troop = {}
            for troop in data["troops_spawned"]:
                troop_id_str = str(troop["troop_id"])
                troop_type = troop["troop_type"].lower()
                troopid_to_troop[troop_id_str] = troop_type
            
            # Calculate initial costs
            for troop_id in troopid_to_troop:
                troop_type = troopid_to_troop[troop_id]
                if troop_type in troop_count:
                    troop_count[troop_type] += 1
                    troop_performance[troop_type] -= troop_costs[troop_type]
            
            # Calculate performance based on attacks
            for attack in data["attacks"]:
                # Parse target type
                if "_" in attack["target_type"]:
                    target, team = attack["target_type"].split("_")
                    target = target.lower()
                    team = team.lower()
                    
                    # Convert IDs to strings for comparison
                    attacker_id_str = str(attack["attacker_id"])
                    target_target_id_str = str(attack.get("target_target_id", "")) if attack.get("target_target_id") else ""
                    
                    # Evaluate attack effectiveness
                    if team == "player" and attacker_id_str in troopid_to_troop:
                        troop_type = troopid_to_troop[attacker_id_str]
                        if troop_type in troop_performance and target in troop_max_hp:
                            troop_performance[troop_type] += (attack["damage"] / troop_max_hp[target]) * troop_costs[target] * 1.5
                    
                    elif team == "player" and target_target_id_str in troopid_to_troop:
                        troop_type = troopid_to_troop[target_target_id_str]
                        if troop_type in troop_performance and target in troop_max_hp:
                            troop_performance[troop_type] += (attack["damage"] / troop_max_hp[target]) * troop_costs[target] * 1

        # Calculate average performance per troop type
        for troop_type in troop_performance:
            if troop_count[troop_type] > 0:
                troop_performance[troop_type] /= troop_count[troop_type]
                # Round for display
                troop_performance[troop_type] = round(troop_performance[troop_type], 2)
            else:
                troop_performance[troop_type] = 0
                
        return troop_performance
        
    except Exception as e:
        print(f"Error analyzing replay {replay_path}: {str(e)}")
        return {}


def main():
    # Check if a specific replay file is provided as argument
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        replay_path = sys.argv[1]
        troop_performance = analyze_replay(replay_path)
        print("Troop Performance:")
        for troop_type, performance in troop_performance.items():
            print(f"{troop_type}: {performance:.2f}")
        return
    
    # Otherwise analyze all replays in the folder
    folder_path = "replays"
    replays = []

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
    
    # Process all replays
    all_performance = {
        "giant": 0,
        "knight": 0,
        "goblin": 0,
        "archer": 0
    }
    
    for replay in replays:
        troop_performance = analyze_replay(replay)
        for troop_type, performance in troop_performance.items():
            all_performance[troop_type] += performance
    
    # Average across all replays
    if replays:
        for troop_type in all_performance:
            all_performance[troop_type] /= len(replays)
    best_troop = max(all_performance.items(), key=lambda x: x[1])[0]
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.abspath(os.path.join(project_root)))
    from use import generate_response, load_fine_tuned_model  # Correct import syntax
    model, tokenizer = load_fine_tuned_model()
    prompt = f"Tips for countering {best_troop.capitalize()}: in Clash Royale"
    tips = generate_response(model, tokenizer, prompt)
    print("Average Troop Performance:")
    for troop_type, performance in all_performance.items():
        print(f"{troop_type}: {performance:.2f}")
    print(f"Tips for countering {best_troop.capitalize()}: {tips}")

if __name__ == "__main__":
    main()