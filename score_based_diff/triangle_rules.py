import pandas as pd

def check_triangle_mutant(csv_path):
    # Use try-except block in case some mutant files don't exist yet
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        return False
        
    is_mutated = False 
    
    for index, row in df.iterrows():
        # --- 1. Load Variables ---
        a = row['in_a']
        b = row['in_b']
        c = row['in_c']
        out_type = row['out_type']
        out_angle = row['out_angle']
        
        # Track which rules break on this specific row
        violated_rules = []
        
        # --- 2. Global Bounds Validation ---
        if out_type not in [1, 2, 3]: 
            violated_rules.append("return.type one of { 1, 2, 3 }")
            
        if out_angle not in [1, 2, 3]: 
            violated_rules.append("return.angle one of { 1, 2, 3 }")

        # --- 3. Conditional Rules (Implications) ---
        
        # IF Angle == 1 (Acute)
        if out_angle == 1:
            if not (out_type >= 1): 
                violated_rules.append("(return.angle == 1) ==> (return.type >= return.angle)")
                
        # IF Angle == 2 (Right)
        if out_angle == 2:
            if not (out_type <= 2): 
                violated_rules.append("(return.angle == 2) ==> (return.type <= return.angle)")
            if out_type not in [1, 2]: 
                violated_rules.append("(return.angle == 2) ==> (return.type one of { 1, 2 })")
                
        # IF Angle == 3 (Obtuse)
        if out_angle == 3:
            if not (out_type < 3): 
                violated_rules.append("(return.angle == 3) ==> (return.type < return.angle)")
            if out_type not in [1, 2]: 
                violated_rules.append("(return.angle == 3) ==> (return.type one of { 1, 2 })")

        # IF Type == 1 (Scalene)
        if out_type == 1:
            if not (1 <= out_angle): 
                violated_rules.append("(return.type == 1) ==> (1 <= return.angle)")
            
        # IF Type == 3 (Equilateral)
        if out_type == 3:
            if a != b: 
                violated_rules.append("(return.type == 3) ==> (arg0.a == arg0.b)")
            if a != c: 
                violated_rules.append("(return.type == 3) ==> (arg0.a == arg0.c)")
            if out_angle != 1: 
                violated_rules.append("(return.type == 3) ==> (return.angle == 1)")
            if not (out_type > out_angle): 
                violated_rules.append("(return.type == 3) ==> (return.type > return.angle)")

        # --- Early Exit ---
        # If any rule is broken, the file is confirmed as mutated.
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
    mutant_flag = check_triangle_mutant(f'mutants/tri_mutant/triangle_mutant_{index}_test.csv')
    print(f"Was this file {index} mutated according to Daikon? {mutant_flag}\n")