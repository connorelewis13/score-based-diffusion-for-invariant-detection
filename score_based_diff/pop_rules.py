import pandas as pd

def check_pop_mutant(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        return False

    is_mutated = False 
    
    for index, row in df.iterrows():
        # --- 1. Load Pointer Variables ---
        in_ptr = row['in_ptr']
        out_ptr = row['out_ptr']
        
        # Track which rules break on this specific row
        violated_rules = []
        
        # --- 2. Check Pointer Logic ---
        if in_ptr < 1: 
            violated_rules.append("arg0.ptr >= 1")
        
        if out_ptr < 0: 
            violated_rules.append("return.ptr >= 0")
            
        if in_ptr - out_ptr - 1 != 0: 
            violated_rules.append("arg0.ptr - return.ptr - 1 == 0")
            
        if not (in_ptr > row['out_v16']): 
            violated_rules.append("arg0.ptr > return.v16")
        
        # --- 3. Check V1 Special Rules ---
        if row['in_v1'] < 1: 
            violated_rules.append("arg0.v1 >= 1")
            
        if row['in_v1'] != 0 and row['out_v1'] % row['in_v1'] != 0: 
            violated_rules.append("return.v1 % arg0.v1 == 0")

        # --- 4. Check V1 to V16 Iterative Rules ---
        for i in range(1, 17):
            in_vi = row[f'in_v{i}']
            out_vi = row[f'out_v{i}']
            out_v16 = row['out_v16']
            
            if i >= 2 and in_vi < 0: 
                violated_rules.append(f"arg0.v{i} >= 0")
                
            if not (in_vi >= out_vi): 
                violated_rules.append(f"arg0.v{i} >= return.v{i}")
                
            if not (in_vi >= out_v16): 
                violated_rules.append(f"arg0.v{i} >= return.v16")
                
            if not (out_vi >= out_v16): 
                violated_rules.append(f"return.v{i} >= return.v16")

            if i <= 15 and out_vi < 0: 
                violated_rules.append(f"return.v{i} >= 0")

        # --- 5. Check V16 Special Out Rule ---
        if row['out_v16'] != 0: 
            violated_rules.append("return.v16 == 0")

        # --- Early Exit ---
        # If the mutant broke any rule above, flag it and stop checking rows
        if violated_rules:
            is_mutated = True
            print(f"Mutant caught in {csv_path} at row {index}!")
            print("Violated Rules:")
            for rule in violated_rules:
                print(f"  - {rule}")
            break 

    return is_mutated

for i in range(4):
    index = i + 1
    mutant_flag = check_pop_mutant(f'mutants/pop_mutant/pop_mutant_{index}_test.csv')
    print(f"Index {index} is a mutant: {mutant_flag}\n")