##Croq: Dumb it down until I've a clear idea of the source of the ownership and licence of this code

class Hypernetwork:
    filename = None
    name = None

    def __init__(self, name=None, enable_sizes=None):
        self.filename = None
        self.name = name
        self.layers = {}
        self.step = 0
        self.sd_checkpoint = None
        self.sd_checkpoint_name = None

    def weights(self):
        pass

    def save(self, filename):
        pass

    def load(self, filename):
        pass

def list_hypernetworks(path):
    return {}

def load_hypernetwork(filename):
    pass

def apply_hypernetwork(hypernetwork, context, layer=None):
    return context, context

def attention_CrossAttention_forward(self, x, context=None, mask=None):
    pass

def train_hypernetwork(hypernetwork_name, learn_rate, data_root, log_directory, steps, create_image_every, save_hypernetwork_every, template_file, preview_image_prompt):
    pass

