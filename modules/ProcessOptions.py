import random

def seed_to_int(s):
    if type(s) is int:
        return s
    if s is None or s == '':
        return random.randint(0, 2**32 - 1)
    n = abs(int(s) if s.isdigit() else random.Random(s).randint(0, 2**32 - 1))
    while n >= 2**32:
        n = n >> 32
    return n

class ProcessOptions:
    def __init__(self, json = {}):
        self.prompt = json.get("prompt", "") # F+B
        self.prompt2 = json.get("prompt2", "") # F+B
        self.prompt2_strength = json.get("prompt2Strength", 0) # F+B
        self.negative_prompt = json.get("negativePrompt", "") # F+B
        self.prompt_style = json.get("promptStyle", "") # B
        self.prompt_style2 = json.get("promptStyle2", "") # B
        self.sampler = json.get("sampler", "DDIM") # F+B
        self.n_iter = json.get("nbImages", 1) # F+B
        self.height = json.get("height", 512) # F+B
        self.width = json.get("width", 512) # F+B
        self.steps = json.get("samplingSteps", 50) # F+B
        self.cfg_scale = json.get("classifierStrength", 7.5) # F+B
        self.seed = seed_to_int(json.get("seed")) # F+B
        self.subseed = seed_to_int(json.get("subseed")) # F+B
        self.subseed_strength = json.get("subseedStrength", 0.0) # F+B
        seed_resize = json.get("resizeSeed", False)
        if seed_resize:
            self.seed_resize_from_h = 512
            self.seed_resize_from_w = 512
        else:
            self.seed_resize_from_h = json.get("seedResizeFromH", 0) # B
            self.seed_resize_from_w = json.get("seedResizeFromW", 0) # B
        self.batch_size = json.get("batchSize", 1) # B
        self.restore_faces = json.get("restoreFaces", False) # B+F
        self.saveLoopback = json.get("saveLoopback", False) # F
        self.use_alpha = json.get("useAlpha", False) # B
        self.mask_blur = json.get("maskBlur", 0) # 
        self.tiling = json.get("tiling", False) # B+F
        self.denoising_strength = json.get("denoiserStrength", 0.75) # F
        self.inpainting_fill = json.get("inpaintingFill", "fill") # B
        self.resize_mode = json.get("resizeMode", "Just resize") # B
        self.inpaint_full_res = json.get("inpaintingFullRes", True) # B
        self.inpaint_mask = json.get("inpaintMask", True) # B
        self.denoiserStrengthFactor = json.get("denoiserStrengthFactor", 0.5) # F
        self.nbLoopback = json.get("nbLoopback", 0)  # F
        self.interpolate_by = json.get("interpolateBy", None)
        self.perlin_strength = json.get("perlinStrength", 0.0)
        self.perlin_octave = json.get("perlinOctave", 12.0)
        
    