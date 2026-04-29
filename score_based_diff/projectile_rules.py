import pandas as pd

def check_projectile_mutant(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        return False
        
    # Initialize the flag (False = Not Mutated, True = Mutated)
    is_mutated = False 
    
    for index, row in df.iterrows():
        # 1. Load the columns into variables using your exact CSV names
        v0 = row['in_v0']
        angle = row['in_angle']
        
        # Outputs
        time = row['out_time']
        max_height = row['out_max_height']
        final_position = row['out_final_position']
        
        # Track which rules break on this specific row
        violated_rules = []
        
        # 2. Check the Daikon Invariants (Reversed to catch violations)
        
        # --- ENTER / BASIC RULES ---
        if v0 == angle:
            violated_rules.append("arg0.v0 != arg0.angle")
            
        # --- EXIT RULES ---
        if final_position == 0:
            violated_rules.append("return.final_position != 0")
            
        if not (v0 > time):
            violated_rules.append("arg0.v0 > return.time")
            
        if not (v0 > max_height):
            violated_rules.append("arg0.v0 > return.max_height")
            
        if v0 == final_position:
            violated_rules.append("arg0.v0 != return.final_position")
            
        if not (angle > time):
            violated_rules.append("arg0.angle > return.time")
            
        if not (angle > max_height):
            violated_rules.append("arg0.angle > return.max_height")
            
        if not (angle > final_position):
            violated_rules.append("arg0.angle > return.final_position")
            
        if time == max_height:
            violated_rules.append("return.time != return.max_height")
            
        if time == final_position:
            violated_rules.append("return.time != return.final_position")
            
        if max_height == final_position:
            violated_rules.append("return.max_height != return.final_position")

        # 3. Early Exit Optimization
        # If the flag was tripped by ANY of the rules above, stop checking!
        if violated_rules:
            is_mutated = True
            print(f"Mutant caught in {csv_path} at row {index}!")
            print("Violated Rules:")
            for rule in violated_rules:
                print(f"  - {rule}")
            break 

    return is_mutated

for i in range(8):
    index = i + 1
    mutant_flag = check_projectile_mutant(f'mutants/proj_mutant/projectile_mutant_{index}_test.csv')
    print(f"Was Index {index} mutated according to Daikon? {mutant_flag}\n")