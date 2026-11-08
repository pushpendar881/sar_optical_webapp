import torch
import torch.nn as nn


class ResnetBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.block = nn.Sequential(
            nn.ReflectionPad2d(1), nn.Conv2d(dim, dim, 3), nn.InstanceNorm2d(dim), nn.ReLU(True),
            nn.ReflectionPad2d(1), nn.Conv2d(dim, dim, 3), nn.InstanceNorm2d(dim),
        )

    def forward(self, x):
        return x + self.block(x)


class ResnetGenerator(nn.Module):
    """Must match the training-notebook architecture exactly (in_ch=1, out_ch=3, ngf=64, n_blocks=9)."""
    def __init__(self, in_ch=1, out_ch=3, ngf=64, n_blocks=9):
        super().__init__()
        model = [nn.ReflectionPad2d(3), nn.Conv2d(in_ch, ngf, 7), nn.InstanceNorm2d(ngf), nn.ReLU(True)]
        n_down = 2
        for i in range(n_down):
            mult = 2 ** i
            model += [nn.Conv2d(ngf * mult, ngf * mult * 2, 3, stride=2, padding=1),
                      nn.InstanceNorm2d(ngf * mult * 2), nn.ReLU(True)]
        mult = 2 ** n_down
        for _ in range(n_blocks):
            model += [ResnetBlock(ngf * mult)]
        for i in range(n_down):
            mult = 2 ** (n_down - i)
            model += [nn.ConvTranspose2d(ngf * mult, int(ngf * mult / 2), 3, stride=2, padding=1, output_padding=1),
                      nn.InstanceNorm2d(int(ngf * mult / 2)), nn.ReLU(True)]
        model += [nn.ReflectionPad2d(3), nn.Conv2d(ngf, out_ch, 7), nn.Tanh()]
        self.model = nn.Sequential(*model)

    def forward(self, x):
        return self.model(x)


def load_generator(checkpoint_path, device):
    """Load generator model with robust error handling - matches working inference script"""
    try:
        print(f"Loading checkpoint from: {checkpoint_path}")
        G_AB = ResnetGenerator(in_ch=1, out_ch=3, ngf=64, n_blocks=9).to(device)
        
        # Load checkpoint with error handling - match working inference script
        ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)
        
        # Handle different checkpoint formats
        if isinstance(ckpt, dict) and "G_AB" in ckpt:
            state_dict = ckpt["G_AB"]
        elif isinstance(ckpt, dict) and "state_dict" in ckpt:
            state_dict = ckpt["state_dict"]
        else:
            state_dict = ckpt
            
        G_AB.load_state_dict(state_dict)
        G_AB.eval()
        
        print(f"✅ Model loaded successfully on {device.upper()}")
        return G_AB
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        if device == 'cuda':
            print("⚠️  Trying CPU fallback...")
            return load_generator(checkpoint_path, 'cpu')
        raise
