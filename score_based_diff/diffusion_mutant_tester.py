import numpy as np
import pandas as pd
import os, math
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
import argparse
from dataloader import FunctionDataset
from model import FF

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("--experiment", type=str, choices=['pop', 'push', 'triangle', 'projectile'], required=True)
parser.add_argument("--batch_size", type=int, default=2048)
parser.add_argument("--conditioning_type", type=int, default=2) # do not change!!!
parser.add_argument("--hidden_units", type=int, default=2048)
parser.add_argument("--n_layers", type=int, default=2)
parser.add_argument("--activation", type=int, default=0)
parser.add_argument("--id", type=int, default=20)
parser.add_argument("--sigma_min", type=float, default=0.01)
parser.add_argument("--sigma_max", type=float, default=1.0)
parser.add_argument("--n_steps", type=int, default=10)
parser.add_argument("--normalize", type=int, default=1)
parser.add_argument("--threshold_level", type=str, default='p99', choices=['p99', 'p99.5'], help="Which threshold to use for detection")
args = parser.parse_args()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 1. Recreate Sigmas
sigmas = torch.exp(torch.linspace(start=math.log(args.sigma_max), end=math.log(args.sigma_min), steps=args.n_steps)).to(device)

# 3. Load Train Data purely for Normalization Statistics & Column Names
train_data_path = f'data/{args.experiment}_train2.csv'

temp_df = pd.read_csv(train_data_path, nrows=0)
csv_target_cols = [col for col in temp_df.columns if col.startswith('out_')]

if args.experiment == 'triangle':
    # Account for the one-hot encoding expansion in the triangle dataset
    target_names = [
        'out_type_Scalene', 'out_type_Isosceles', 'out_type_Equilateral',
        'out_angle_Acute', 'out_angle_Right', 'out_angle_Obtuse'
    ]
else:
    target_names = csv_target_cols
    
def get_var_name(idx):
    if idx < len(target_names):
        return target_names[idx]
    return f"Target_Var_{idx}"
# -------------------------------------------------------------

train_dataset = FunctionDataset(train_data_path)

if args.experiment == 'triangle':
    col1 = train_dataset.target[:, 0].to(torch.int64)
    col2 = train_dataset.target[:, 1].to(torch.int64)
    if col1.max() > 0: col1 -= 1
    if col2.max() > 0: col2 -= 1
    one_hot_1 = F.one_hot(col1, num_classes=3).float()
    one_hot_2 = F.one_hot(col2, num_classes=3).float()
    train_dataset.target = torch.cat([one_hot_1, one_hot_2], dim=1)

y_mean = train_dataset.condition.mean(dim=0, keepdim=True)
y_std  = train_dataset.condition.std(dim=0,  keepdim=True)
if args.experiment != 'triangle':
    x_mean = train_dataset.target.mean(dim=0, keepdim=True)
    x_std  = train_dataset.target.std(dim=0,  keepdim=True)

n_output = train_dataset.target.shape[1]
problem_params_dim = train_dataset.condition.shape[1]

# 4. Initialize and Load Model
if args.conditioning_type == 0: n_input = n_output
elif args.conditioning_type == 1: n_input = n_output + 1
else: n_input = n_output + 1 + problem_params_dim

layer_dims = [n_input] + [args.hidden_units] * args.n_layers + [n_output]
act_funcs = {0: torch.nn.ReLU, 1: torch.nn.Tanh, 2: torch.nn.SiLU}
model = FF(layer_dims, activation=act_funcs[args.activation]).to(device)
model.load_state_dict(torch.load(f'./models/model_{args.id}_{args.experiment}.pt', map_location=device))
model.eval()

val_data_path = f'data/{args.experiment}_val2.csv'
val_dataset = FunctionDataset(val_data_path)

if args.experiment == 'triangle':
    col1 = val_dataset.target[:, 0].to(torch.int64)
    col2 = val_dataset.target[:, 1].to(torch.int64)
    if col1.max() > 0: col1 -= 1
    if col2.max() > 0: col2 -= 1
    one_hot_1 = F.one_hot(col1, num_classes=3).float()
    one_hot_2 = F.one_hot(col2, num_classes=3).float()
    val_dataset.target = torch.cat([one_hot_1, one_hot_2], dim=1)

if args.normalize == 1:
    val_dataset.condition = (val_dataset.condition - y_mean) / (y_std + 1e-8)
    if args.experiment != 'triangle':
        val_dataset.target = (val_dataset.target - x_mean) / (x_std + 1e-8)

val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)

all_norms = {sigma_idx: [] for sigma_idx in range(args.n_steps)}

with torch.no_grad():
    for x, y in val_loader:
        x, y = x.to(device), y.to(device)
        for sigma_idx in range(args.n_steps):
            idx = torch.full((x.size(0), 1), sigma_idx, dtype=torch.long).to(device)
            chosen_sigmas = sigmas[idx]
            ln_sigma = torch.log(chosen_sigmas)
            x_in = torch.cat([x, ln_sigma, y], dim=1)
            pred_score = model(x_in)
            l2_norms = torch.norm(pred_score, dim=1)
            all_norms[sigma_idx].append(l2_norms.cpu().numpy())

percentile_map = {'p99': 99, 'p99.5': 99.5}
pct = percentile_map[args.threshold_level]
thresholds = torch.tensor([
    np.percentile(np.concatenate(all_norms[i]), pct)
    for i in range(args.n_steps)
], dtype=torch.float32).to(device)

print(f"Thresholds computed from validation set ({args.threshold_level}):")
for i, t in enumerate(thresholds):
    print(f"  sigma[{i}]={sigmas[i].item():.4f} → threshold={t.item():.4f}")

# Global list to store dataframes for the CSV
all_summary_results = []

# 5. Define Evaluation Function
def evaluate_dataset(file_path, dataset_name):
    if not os.path.exists(file_path):
        return
    
    ds = FunctionDataset(file_path)
    
    if args.experiment == 'triangle':
        col1 = ds.target[:, 0].to(torch.int64)
        col2 = ds.target[:, 1].to(torch.int64)
        if col1.max() > 0: col1 -= 1
        if col2.max() > 0: col2 -= 1
        one_hot_1 = F.one_hot(col1, num_classes=3).float()
        one_hot_2 = F.one_hot(col2, num_classes=3).float()
        ds.target = torch.cat([one_hot_1, one_hot_2], dim=1)
        
    if args.normalize == 1:
        ds.condition = (ds.condition - y_mean) / (y_std + 1e-8)
        if args.experiment != 'triangle':
            ds.target = (ds.target - x_mean) / (x_std + 1e-8)

    dataloader = DataLoader(ds, batch_size=args.batch_size, shuffle=False)
    
    total_samples = len(ds)
    flagged_matrix = torch.zeros((total_samples, args.n_steps), dtype=torch.bool).to(device)
    
    # Matrix to store the index of the variable with the highest absolute gradient
    max_grad_matrix = torch.zeros((total_samples, args.n_steps), dtype=torch.long).to(device)
    
    with torch.no_grad():
        start_idx = 0
        for x, y in dataloader:
            x, y = x.to(device), y.to(device)
            batch_size = x.size(0)
            
            for sigma_idx in range(args.n_steps):
                idx = torch.full((batch_size, 1), sigma_idx, dtype=torch.long).to(device)
                chosen_sigmas = sigmas[idx]
                
                if args.conditioning_type == 0: x_in = x
                elif args.conditioning_type == 1: x_in = torch.cat([x, idx], dim=1)
                elif args.conditioning_type == 2:
                    ln_sigma = torch.log(chosen_sigmas)
                    x_in = torch.cat([x, ln_sigma, y], dim=1)
                    
                pred_score = model(x_in)
                l2_norms = torch.norm(pred_score, dim=1)
                
                is_anomaly = l2_norms > thresholds[sigma_idx]
                flagged_matrix[start_idx:start_idx+batch_size, sigma_idx] = is_anomaly
                
                # Find which dimension of the predicted score has the largest absolute magnitude
                max_grad_matrix[start_idx:start_idx+batch_size, sigma_idx] = torch.argmax(torch.abs(pred_score), dim=1)
                
            start_idx += batch_size

    # --- AGGREGATION LOGIC ---
    noise_level_percentages = (flagged_matrix.sum(dim=0).float() / total_samples) * 100
    overall_flagged = flagged_matrix.any(dim=1)
    total_flagged_count = overall_flagged.sum().item()
    overall_percentage = (total_flagged_count / total_samples) * 100
    
    # --- ANOMALY ATTRIBUTION LOGIC ---
    flagged_flat = flagged_matrix.view(-1)
    max_grad_flat = max_grad_matrix.view(-1)
    
    flagged_vars = max_grad_flat[flagged_flat]
    
    if len(flagged_vars) > 0:
        var_counts = torch.bincount(flagged_vars, minlength=n_output)
        sorted_vars = torch.argsort(var_counts, descending=True).cpu().numpy()
        
        # --- NEW: Map indices to CSV variable names ---
        top_1 = get_var_name(sorted_vars[0]) if len(sorted_vars) > 0 else "None"
        top_2 = get_var_name(sorted_vars[1]) if len(sorted_vars) > 1 else "None"
        top_3 = get_var_name(sorted_vars[2]) if len(sorted_vars) > 2 else "None"
    else:
        top_1, top_2, top_3 = "None", "None", "None"
    
    # Create the single-row dictionary for this file
    summary = {
        'Experiment': args.experiment,
        'Threshold': args.threshold_level,
        'Dataset': dataset_name
    }
    
    # Add noise level columns
    for i in range(args.n_steps):
        summary[f'Noise_Level_{i}_Pct'] = noise_level_percentages[i].item()
    
    summary['Total_Overall_Pct'] = overall_percentage
    
    # Add the top variables to the CSV
    summary['Most_Common_Var'] = top_1
    summary['Second_Most_Common_Var'] = top_2
    summary['Third_Most_Common_Var'] = top_3
    
    all_summary_results.append(summary)

    print(f"{dataset_name.ljust(15)} | Flagged: {total_flagged_count}/{total_samples} | Detection Rate: {overall_percentage:.2f}% | Top Var: {top_1}")


# 6. Run Evaluation
print("="*60)
print(f"EVALUATING {args.experiment.upper()} (Summary Mode)")
print("="*60)

evaluate_dataset(f'data/{args.experiment}_test2.csv', "Clean Test")

num_exp = 0

if args.experiment == 'pop':
    mutant_folder = f'mutants/pop_mutant/'
    num_exp = 4
elif args.experiment =='push':
    mutant_folder = f'mutants/push_mutant/'
    num_exp = 4
elif args.experiment =='projectile':
    mutant_folder = f'mutants/proj_mutant/'
    num_exp = 8
elif args.experiment =='triangle':
    mutant_folder = f'mutants/tri_mutant/'
    num_exp = 8

for i in range(0, num_exp): 
    index = i + 1
    mutant_path = f'{mutant_folder}{args.experiment}_mutant_{index}_test.csv'
    evaluate_dataset(mutant_path, f"Mutant {i}")
print("="*60)

final_df = pd.DataFrame(all_summary_results)
out_csv_name = f'threshold_flag_results/summary_results_{args.experiment}_id{args.id}_{args.threshold_level}.csv'
final_df.to_csv(out_csv_name, index=False)
print(f"\nSaved summary (one row per file) to: {out_csv_name}")