import numpy as np
import pandas as pd
import os, math
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
import argparse
from dataloader import FunctionDataset
from model import FF
from scipy.stats import ks_2samp

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument("--experiment", type=str, choices=['pop', 'push', 'triangle', 'projectile'], required=True)
parser.add_argument("--batch_size", type=int, default=2048)
parser.add_argument("--conditioning_type", type=int, default=2)
parser.add_argument("--hidden_units", type=int, default=2048)
parser.add_argument("--n_layers", type=int, default=2)
parser.add_argument("--activation", type=int, default=0)
parser.add_argument("--id", type=int, default=20)
parser.add_argument("--sigma_min", type=float, default=0.01)
parser.add_argument("--sigma_max", type=float, default=1.0)
parser.add_argument("--n_steps", type=int, default=10)
parser.add_argument("--normalize", type=int, default=1)
args = parser.parse_args()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 1. Recreate Sigmas
sigmas = torch.exp(torch.linspace(start=math.log(args.sigma_max), end=math.log(args.sigma_min), steps=args.n_steps)).to(device)

# 2. Load Train Data purely for Normalization Statistics
train_data_path = f'data/{args.experiment}_train2.csv'
train_dataset = FunctionDataset(train_data_path)

if args.experiment == 'triangle':
    col1 = train_dataset.target[:, 0].to(torch.int64)
    col2 = train_dataset.target[:, 1].to(torch.int64)
    if col1.min() > 0: col1 -= col1.min()
    if col2.min() > 0: col2 -= col2.min()
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

# 3. Initialize and Load Model
if args.conditioning_type == 0: n_input = n_output
elif args.conditioning_type == 1: n_input = n_output + 1
else: n_input = n_output + 1 + problem_params_dim

layer_dims = [n_input] + [args.hidden_units] * args.n_layers + [n_output]
act_funcs = {0: torch.nn.ReLU, 1: torch.nn.Tanh, 2: torch.nn.SiLU}
model = FF(layer_dims, activation=act_funcs[args.activation]).to(device)
model.load_state_dict(torch.load(f'./models/model_{args.id}_{args.experiment}.pt', map_location=device))
model.eval()

# Global list to store results
all_summary_results = []

# 4. Define Evaluation Function to get full matrices
def get_dataset_matrices(file_path):
    if not os.path.exists(file_path):
        return None
    
    ds = FunctionDataset(file_path)
    
    if args.experiment == 'triangle':
        col1 = ds.target[:, 0].to(torch.int64)
        col2 = ds.target[:, 1].to(torch.int64)
        if col1.min() > 0: col1 -= col1.min()
        if col2.min() > 0: col2 -= col2.min()
        one_hot_1 = F.one_hot(col1, num_classes=3).float()
        one_hot_2 = F.one_hot(col2, num_classes=3).float()
        ds.target = torch.cat([one_hot_1, one_hot_2], dim=1)
        
    if args.normalize == 1:
        ds.condition = (ds.condition - y_mean) / (y_std + 1e-8)
        if args.experiment != 'triangle':
            ds.target = (ds.target - x_mean) / (x_std + 1e-8)

    dataloader = DataLoader(ds, batch_size=args.batch_size, shuffle=False)
    total_samples = len(ds)
    
    # Keep the full matrix of [samples, noise_levels]
    all_l2_norms = torch.zeros((total_samples, args.n_steps)).to(device)
    
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
                all_l2_norms[start_idx:start_idx+batch_size, sigma_idx] = l2_norms
                
            start_idx += batch_size

    return all_l2_norms

# 5. Helper to run KS Test across all noise levels and save results
def evaluate_and_compare(target_path, dataset_name, baseline_matrix):
    target_matrix = get_dataset_matrices(target_path)
    if target_matrix is None:
        print(f"File not found: {target_path}")
        return

    n = args.n_steps
    alpha = 0.01

    row_data = {
        'Experiment': args.experiment,
        'Dataset': dataset_name,
    }

    # Per-noise-level KS tests
    p_values = []
    for step in range(n):
        base_step_scores = baseline_matrix[:, step].cpu().numpy()
        targ_step_scores = target_matrix[:, step].cpu().numpy()

        step_ks, step_p = ks_2samp(base_step_scores, targ_step_scores)
        p_values.append(step_p)

        row_data[f'Noise_{step}_KS_Stat'] = step_ks
        row_data[f'Noise_{step}_P_Value'] = step_p

    row_data['Union_Bonferroni'] = bool(any(p < alpha / n for p in p_values))

    print(f"{dataset_name.ljust(15)} | Bonferroni Detected: {row_data['Union_Bonferroni']}")

    all_summary_results.append(row_data)

# 6. Run Evaluation
print("="*80)
print(f"EVALUATING {args.experiment.upper()} (KS-Test vs Validation Set per Noise Level)")
print("="*80)

# Load baseline (Validation Set)
val_path = f'data/{args.experiment}_val2.csv'
val_matrix = get_dataset_matrices(val_path)

if val_matrix is None:
    print(f"ERROR: Validation data not found at {val_path}")
    exit()

# Test vs Clean Test Set
test_path = f'data/{args.experiment}_test2.csv'
evaluate_and_compare(test_path, "Clean Test", val_matrix)
print("-" * 80)

# Folder Logic
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

# Test vs Mutants
for i in range(0, num_exp): 
    index = i + 1
    mutant_path = f'{mutant_folder}{args.experiment}_mutant_{index}_test.csv'
    evaluate_and_compare(mutant_path, f"Mutant {index}", val_matrix)
    
print("="*80)

# 7. Save Final Master CSV
if all_summary_results:
    # Make sure output directory exists
    os.makedirs('ks_test_results', exist_ok=True)
    
    final_df = pd.DataFrame(all_summary_results)
    out_csv_name = f'ks_test_results/kstest_detailed_{args.experiment}_id{args.id}.csv'
    final_df.to_csv(out_csv_name, index=False)
    print(f"\nSaved detailed summary to: {out_csv_name}")