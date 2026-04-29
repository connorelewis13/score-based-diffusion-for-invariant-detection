import pandas as pd

def check_push_mutant(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        return False

    is_mutated = False 
    
    for index, row in df.iterrows():
        # --- 1. Load Core Variables ---
        in_ptr = row['in_ptr']
        out_ptr = row['out_ptr']
        in_newValue = row['in_newValue']
        in_v16 = row['in_v16']
        out_v16 = row['out_v16']
        
        # Track which rules break on this specific row
        violated_rules = []
        
        # --- 2. Check Pointer Logic ---
        if in_ptr < 0: 
            violated_rules.append("arg0.ptr >= 0")
            
        if out_ptr < 1: 
            violated_rules.append("return.ptr >= 1")
            
        if in_ptr - out_ptr + 1 != 0: 
            violated_rules.append("arg0.ptr - return.ptr + 1 == 0")
            
        if not (in_ptr >= in_v16): 
            violated_rules.append("arg0.ptr >= arg0.v16")

        # --- 3. Check newValue (arg1) Logic ---
        if in_newValue < 1: 
            violated_rules.append("arg1 >= 1")
            
        if not (in_v16 < in_newValue): 
            violated_rules.append("arg0.v16 < arg1 / arg0.v16 < orig(arg1)")
            
        if in_newValue != 0 and out_v16 % in_newValue != 0: 
            violated_rules.append("return.v16 % orig(arg1) == 0")
            
        if not (out_v16 <= in_newValue): 
            violated_rules.append("return.v16 <= orig(arg1)")

        # --- 4. Check Special Case: V16 ---
        if in_v16 != 0: 
            violated_rules.append("arg0.v16 == 0")
            
        if out_v16 < 0: 
            violated_rules.append("return.v16 >= 0")
            
        if not (in_v16 < out_ptr): 
            violated_rules.append("arg0.v16 < return.ptr")

        # --- 5. Check Iterative Rules (V1 to V15) ---
        for i in range(1, 16):
            in_vi = row[f'in_v{i}']
            out_vi = row[f'out_v{i}']
            
            if in_vi < 0: 
                violated_rules.append(f"arg0.v{i} >= 0")
                
            if i > 1 and out_vi < 0: 
                violated_rules.append(f"return.v{i} >= 0")
                
            if not (in_vi >= in_v16): 
                violated_rules.append(f"arg0.v{i} >= arg0.v16")
                
            if not (in_vi <= out_vi): 
                violated_rules.append(f"arg0.v{i} <= return.v{i}")
                
            if i > 1 and not (in_v16 <= out_vi): 
                violated_rules.append(f"arg0.v16 <= return.v{i}")

        # --- 6. Check Special Case: V1 ---
        if row['out_v1'] < 1: 
            violated_rules.append("return.v1 >= 1")
            
        if row['out_v1'] != 0 and row['in_v1'] % row['out_v1'] != 0: 
            violated_rules.append("arg0.v1 % return.v1 == 0")
            
        if not (in_v16 < row['out_v1']): 
            violated_rules.append("arg0.v16 < return.v1")

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

for i in range(4):
    index = i + 1
    mutant_flag = check_push_mutant(f'mutants/push_mutant/push_mutant_{index}_test.csv')
    print(f"Index {index} is a mutant: {mutant_flag}\n")