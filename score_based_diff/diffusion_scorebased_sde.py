import numpy as np
import pandas as pd
import os, math
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from dataloader import FunctionDataset
from model import FF
#import matplotlib.pyplot as plt
import random
from torch.utils.data import DataLoader
import argparse

# Parse args
parser = argparse.ArgumentParser()
# Setting parameters
parser.add_argument("--experiment", type=str, choices=['pop', 'push', 'triangle', 'projectile'], help="Experiment setting")
parser.add_argument("--batch_size", type=int, default=2048, help="Random seed")
parser.add_argument("--max_epochs", type=int, default=1000, help="Random seed")
parser.add_argument("--conditioning_type", type=int, default=2, help="Random seed")
# Model parameters
parser.add_argument("--eps", type=float, default=1.5e-5, help="Epsilon of step size")

parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
parser.add_argument("--hidden_units", type=int, default=2048, help="Hidden units of the model")
parser.add_argument("--n_layers", type=int, default=2, help="Random seed")
parser.add_argument("--seed", type=int, default=2, help="Random seed")
parser.add_argument("--optimizer", type=int, default=0, help="Random seed")
parser.add_argument("--activation", type=int, default=0, help="Random seed")
parser.add_argument("--id", type=int, default=20, help="Hidden units of the model")

parser.add_argument("--sigma_min", type=float, default=0.01, help="Sigma min of Langevin dynamic")
parser.add_argument("--sigma_max", type=float, default=1.0, help="Sigma max of Langevin dynamic")
parser.add_argument("--n_steps", type=int, default=10, help="Langevin steps")
parser.add_argument("--normalize", type=int, default=1, help="Data normalization")

# Training parameters
parser.add_argument("--total_iteration", type=int, default=3000, help="Total training iterations")
parser.add_argument("--display_iteration", type=int, default=150, help="Logging frequency")
# Removed --project argument as it's no longer used

args = parser.parse_args()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

seed = args.seed

train_data_path = f'data/{args.experiment}_train2.csv'
val_data_path = f'data/{args.experiment}_val2.csv'
test_data_path = f'data/{args.experiment}_test2.csv'

train_dataset = FunctionDataset(train_data_path) # Directly use QPDataset
valid_dataset = FunctionDataset(val_data_path) # Directly use QPDataset
test_dataset = FunctionDataset(test_data_path) # Directly use QPDataset

def z_score_normalize(t, mean_vals, std_vals):
    return (t - mean_vals) / (std_vals + 1e-8)

def z_score_denormalize(t, mean_vals, std_vals):
    return t * std_vals + mean_vals

train_dataset = FunctionDataset(train_data_path)
valid_dataset = FunctionDataset(val_data_path)
test_dataset = FunctionDataset(test_data_path)


# print(train_dataset.target[:5])
# --- NEW CONCATENATED ONE-HOT ENCODING BLOCK ---
if args.experiment == 'triangle':
    num_classes_per_column = 3 
    
    for ds in [train_dataset, valid_dataset, test_dataset]:
        # Extract column 1 (e.g., Angle Type) and column 2 (e.g., Side Type)
        col1 = ds.target[:, 0].to(torch.int64)
        col2 = ds.target[:, 1].to(torch.int64)
        
        # Shift from 1-3 to 0-2 for F.one_hot
        if col1.max() > 0: 
            col1 -= 1
        if col2.max() > 0: 
            col2 -= 1
            
        # Create the one-hot vectors for each column (Shape: [Batch, 3])
        one_hot_1 = F.one_hot(col1, num_classes=num_classes_per_column).float()
        one_hot_2 = F.one_hot(col2, num_classes=num_classes_per_column).float()
        
        # Concatenate them along the feature dimension (Shape becomes [Batch, 6])
        ds.target = torch.cat([one_hot_1, one_hot_2], dim=1)

# Update n_output dynamically (this will cleanly read '6' now)
n_output = train_dataset.target.shape[1]
problem_params_dim = train_dataset.condition.shape[1]
# -----------------------------------
# print(train_dataset.target[:5])


if args.normalize == 1:
    # ALWAYS normalize the condition (the 'in' columns)
    y_mean = train_dataset.condition.mean(dim=0, keepdim=True)
    y_std  = train_dataset.condition.std(dim=0,  keepdim=True)
    for ds in [train_dataset, valid_dataset, test_dataset]:
        ds.condition = (ds.condition - y_mean) / (y_std + 1e-8)

    # ONLY normalize the target if it is NOT the one-hot triangle class
    if args.experiment != 'triangle':
        x_mean = train_dataset.target.mean(dim=0, keepdim=True)
        x_std  = train_dataset.target.std(dim=0,  keepdim=True)
        for ds in [train_dataset, valid_dataset, test_dataset]:
            ds.target = (ds.target - x_mean) / (x_std + 1e-8)

# print(train_dataset.target[:5])

dataloader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
valid_dataloader = DataLoader(valid_dataset, batch_size=len(valid_dataset), shuffle=False)
test_dataloader = DataLoader(test_dataset, batch_size=len(test_dataset), shuffle=False)


# n_output = train_dataset.n
# problem_params_dim = train_dataset.condition.shape[1]


# Now calculate the total input dimension (n_input) for your model based on conditioning_type
# This uses the dynamically determined n_output and problem_params_dim
if args.conditioning_type == 0: # Only x_tilde (the noisy input)
    n_input = n_output
elif args.conditioning_type == 1: # x_tilde + idx (noise level)
    n_input = n_output + 1
else: # x_tilde + idx (noise level) + y (problem parameters)
    n_input = n_output + 1 + problem_params_dim

layer_dims = [n_input] + [args.hidden_units] * args.n_layers + [n_output]

if args.activation == 0:
    act = nn.ReLU
elif args.activation == 1:
    act = nn.Tanh
elif args.activation == 2:
    act = nn.SiLU

# print(train_dataset.target[:5])
# print(train_dataset.condition[:5])


# ---
## DEFINE MODEL
# ---

model = FF(layer_dims, activation=act).to(device = device)

print(model)

if args.optimizer == 0:
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
elif args.optimizer == 1:
    optimizer = optim.SGD(model.parameters(), lr=args.lr)
elif args.optimizer == 2:
    optimizer = optim.RMSprop(model.parameters(), lr=args.lr)
#optimizer = optim.AdamW(model.parameters(), lr=args.lr)


scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=10, min_lr=1e-7
)

epochs = args.max_epochs
patience = 0
max_patience = 100

min_loss = float('inf')
sigma_min = args.sigma_min
sigma_max = args.sigma_max
n_steps = args.n_steps
# sigmas = np.linspace(sigma_max, sigma_min, L, dtype=np.float32)
sigmas = torch.exp(torch.linspace(start=math.log(sigma_max), end=math.log(sigma_min), steps = n_steps)).to(device = device)
epoch_loss = []
valid_loss_list = []
test_loss = 0

# ---
## HYPERPARAMS (no changes needed here)
# ---

# min y = 1/2 xQx + px
# Ax =b
# x | A, b

# Fix validation noise once before training - all sigmas for all examples
with torch.no_grad():
    for val_x, val_y in valid_dataloader:
        val_x, val_y = val_x.to(device), val_y.to(device)

# Repeat each example for every sigma level
val_x_expanded = val_x.repeat_interleave(len(sigmas), dim=0)  # (400*10, 17)
val_y_expanded = val_y.repeat_interleave(len(sigmas), dim=0)  # (400*10, 18)

# Assign each sigma level to each example
sigma_indices = torch.arange(len(sigmas)).repeat(val_x.size(0)).to(device)  # (1500,)
val_sigmas = sigmas[sigma_indices].unsqueeze(1)  # (1500, 1)

val_noise = torch.randn_like(val_x_expanded)
val_x_tilde = val_x_expanded + val_sigmas * val_noise
val_target_score = -1 / val_sigmas * val_noise
val_ln_sigma = torch.log(val_sigmas)
val_x_in = torch.cat([val_x_tilde, val_ln_sigma, val_y_expanded], dim=1)

with torch.no_grad():
    for test_x, test_y in test_dataloader:
        test_x, test_y = test_x.to(device), test_y.to(device)

test_x_expanded = test_x.repeat_interleave(len(sigmas), dim=0)
test_y_expanded = test_y.repeat_interleave(len(sigmas), dim=0)
sigma_indices_test = torch.arange(len(sigmas)).repeat(test_x.size(0)).to(device)
test_sigmas = sigmas[sigma_indices_test].unsqueeze(1)
test_noise = torch.randn_like(test_x_expanded)
test_x_tilde = test_x_expanded + test_sigmas * test_noise
test_target_score = -1 / test_sigmas * test_noise
test_ln_sigma = torch.log(test_sigmas)
test_x_in = torch.cat([test_x_tilde, test_ln_sigma, test_y_expanded], dim=1)


for epoch in range(epochs):
    running_loss = 0.0
    print('='* 80)
    iteration = 0
    model.train()
    for x, y in dataloader:
        x, y = x.to(device), y.to(device)
        # print(x)
        # print(y)
        idx = torch.randint(0, len(sigmas), (x.size(0), 1)).to(device = device)
        #idx = torch.randint(0, len(sigmas)).to(device = device)
        chosen_sigmas = sigmas[idx] # shape (batch, 1)
        noise = torch.randn_like(x, device=device)
        x_tilde = x + chosen_sigmas * noise
        #target_score = (x - x_tilde) / (chosen_sigmas**2)
        target_score = -1/(chosen_sigmas) * noise # same thing as above expression

        #pred_score = model(x_tilde, idx , y) ### NOISE AND PROBLEM PARAEMTERS CONDITIONING
        #pred_score = model(x_tilde, idx)  ### NOISE CONDITIONING

        if args.conditioning_type == 0:
            x_in = x_tilde
        elif args.conditioning_type == 1:
            x_in = torch.cat([x_tilde, idx], dim = 1)
        elif args.conditioning_type == 2:
            ln_sigma = torch.log(chosen_sigmas)
            x_in = torch.cat([x_tilde, ln_sigma, y], dim=1)

        pred_score = model(x_in) ### NO CONDITIONING

        # loss = (pred_score - target_score).square().mean()
        # loss = (torch.square(target_score - pred_score).mean(-1) * (chosen_sigmas**2)).mean()
        loss = (torch.square(target_score - pred_score) * (chosen_sigmas**2)).mean()
        optimizer.zero_grad()
        loss.backward()
        # total_norm = sum(p.grad.data.norm(2).item()**2 for p in model.parameters() if p.grad is not None)**0.5
        # print(f"grad norm: {total_norm:.6f}")
        # print(f"loss: {loss.item():.4f}")
        optimizer.step()
        running_loss += loss.item() * x.size(0)
        iteration+=1
        # if iteration %5 == 0:
        #    print('Checkpoint: Batch loss:{}  Running_loss: {}'.format(loss.item(), running_loss/iteration))
        # print(f"target_score mean: {target_score.mean():.4f}, std: {target_score.std():.4f}")
        # print(f"pred_score mean:   {pred_score.mean():.4f}, std: {pred_score.std():.4f}")
        # print(f"chosen_sigmas min: {chosen_sigmas.min():.4f}, max: {chosen_sigmas.max():.4f}")

    avg_loss = running_loss / len(train_dataset)
    epoch_loss.append(avg_loss)
    if epoch % 1 ==0:
        model.eval()
        with torch.no_grad():
            pred_score = model(val_x_in)
            loss = (torch.square(val_target_score - pred_score) * (val_sigmas**2)).mean()
            valid_loss = loss.item()

            if valid_loss<min_loss:
                min_loss = valid_loss
                print('Saving model...')
                # Ensure models directory exists
                # -------------------------------------------------------------
                os.makedirs('./models/', exist_ok=True)
                # -------------------------------------------------------------
                torch.save(model.state_dict(), f'./models/model_{args.id}_{args.experiment}.pt')
                print('Model saved.')
                patience = 0
            else:
                patience += 1
            if patience == max_patience:
                print('Early stopping...')
                break
            valid_loss_list.append(valid_loss)
            scheduler.step(valid_loss)
            print(f"Epoch {epoch+1}/{epochs}, Train Loss: {avg_loss:.6f}, Val Loss: {valid_loss:.6f}")


# Ensure loss directory exists
# -------------------------------------------------------------
os.makedirs('./loss/', exist_ok=True)
# -------------------------------------------------------------
np.save(f'loss/valid_loss_list_{args.id}_{args.experiment}_norm.npy', valid_loss_list)
np.save(f'loss/train_loss_list_{args.id}_{args.experiment}_norm.npy', epoch_loss)
model.load_state_dict(torch.load(f'./models/model_{args.id}_{args.experiment}.pt'))


model.eval()
with torch.no_grad():
    pred_score = model(test_x_in)
    loss = (torch.square(test_target_score - pred_score) * (test_sigmas**2)).mean()
    test_loss = loss.item()

record = {
    'test loss' : [test_loss],
    'id' : [args.id]
}

df = pd.DataFrame(record)
df.to_csv('MLP_DENOISER_TEST_LOSS_LONG_EPOCHS_AND NORMALIZE.csv',mode='a', header=False, index=False)


model.eval()
all_scores = {sigma_idx: [] for sigma_idx in range(len(sigmas))}

with torch.no_grad():
    for x, y in valid_dataloader:
        x, y = x.to(device), y.to(device)
        for sigma_idx in range(len(sigmas)):
            idx = torch.full((x.size(0), 1), sigma_idx, dtype=torch.long).to(device)
            chosen_sigmas = sigmas[idx]
            if args.conditioning_type == 0:
                x_in = x
            elif args.conditioning_type == 1:
                x_in = torch.cat([x, idx], dim=1)
            elif args.conditioning_type == 2:
                ln_sigma = torch.log(chosen_sigmas)
                x_in = torch.cat([x, ln_sigma, y], dim=1)
            pred_score = model(x_in)
            l2_norms = torch.norm(pred_score, dim=1)
            all_scores[sigma_idx].append(l2_norms.cpu().numpy())
            
rows = []
for sigma_idx in range(len(sigmas)):
    norms = np.concatenate(all_scores[sigma_idx])
    rows.append({
        'sigma_idx': sigma_idx,
        'sigma': sigmas[sigma_idx].item(),
        'p99': float(np.percentile(norms, 99)),
        'p99.5': float(np.percentile(norms, 99.5))
    })

os.makedirs('./thresholds/', exist_ok=True)
pd.DataFrame(rows).to_csv(f'./thresholds/thresholds_{args.id}_{args.experiment}.csv', index=False)
print("Thresholds saved.")
