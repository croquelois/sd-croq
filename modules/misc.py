import torch
import pandas as pd
import numpy as np

def studyTorchTensor(name, x):
    print(f"{name} size:{x.size()}")
    print(f"{name} mean:{torch.mean(x)}")
    print(f"{name} stdev:{torch.std(x)}")
    print(f"{name} min:{torch.min(x)}")
    print(f"{name} max:{torch.max(x)}")

def saveTorchTensor(prompt, x, filename):
    filename = filename + '-tensor.csv'
    x_np = x.cpu().numpy()
    x_df = pd.DataFrame(x_np)
    x_df.to_csv(filename)
    open(filename, 'a').write(prompt)