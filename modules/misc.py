import torch
import pandas as pd
import numpy as np
#CROQ: Broken: from modules.prompt_parser import ScheduledPromptBatch, ScheduledPromptConditioning

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

#CROQ: Broken
#def interpolate_schedule(c1, c2, a):
#    cond1 = c1.schedules[0][0].cond
#    cond2 = c2.schedules[0][0].cond
#    cond = torch.add(torch.mul(cond1, (1-a)), torch.mul(cond2, a))
#    return ScheduledPromptBatch(c1.shape, [[ScheduledPromptConditioning(c1.schedules[0][0].end_at_step, cond)]])
