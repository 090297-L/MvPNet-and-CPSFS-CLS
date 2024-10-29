import math
import torch
import torch.nn.functional as F
from einops import rearrange
import torch.nn as nn


def rescale_to(x, scale_factor: float = 2, interpolation='nearest'):
    return F.interpolate(x, scale_factor=scale_factor, mode=interpolation)

def image2patches(x):
    """b c (hg h) (wg w) -> (hg wg b) c h w"""
    x = rearrange(x, 'b c (hg h) (wg w) -> (hg wg b) c h w', hg=2, wg=2)
    return x

def patches2image(x):
    """(hg wg b) c h w -> b c (hg h) (wg w)"""
    x = rearrange(x, '(hg wg b) c h w -> b c (hg h) (wg w)', hg=2, wg=2)
    return x

class _DSConv(nn.Module):
    """Depthwise Separable Convolutions"""

    def __init__(self, dw_channels, out_channels, stride=1, **kwargs):
        super(_DSConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(dw_channels, dw_channels, 3, stride, 0, groups=dw_channels, bias=False),
            nn.BatchNorm2d(dw_channels),
            nn.ReLU(True),
            nn.Conv2d(dw_channels, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(True)
        )

    def forward(self, x):
        return self.conv(x)

class _DWConv(nn.Module):
    def __init__(self, dw_channels, out_channels, kernel=1, stride=1,padding=0, **kwargs):
        super(_DWConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(dw_channels, out_channels, kernel, stride, padding, groups=dw_channels, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(True)
        )

    def forward(self, x):
        return self.conv(x)

class Mlp(nn.Module):
    """ Multilayer perceptron."""

    def __init__(self, in_features, hidden_features=None, out_features=None, act_layer=nn.GELU, drop=0):
        super().__init__()
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        self.fc1 = nn.Linear(in_features, hidden_features)
        self.act = act_layer()
        self.fc2 = nn.Linear(hidden_features, out_features)
        self.drop = nn.Dropout(drop)

    def forward(self, x):
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.drop(x)
        return x

class PositionEmbeddingSine:
    def __init__(self, num_pos_feats=64, temperature=10000, normalize=False, scale=None):
        super().__init__()
        self.num_pos_feats = num_pos_feats
        self.temperature = temperature
        self.normalize = normalize
        if scale is not None and normalize is False:
            raise ValueError("normalize should be True if scale is passed")
        if scale is None:
            scale = 2 * math.pi
        self.scale = scale
        self.dim_t = torch.arange(0, self.num_pos_feats, dtype=torch.float32, device='cuda')

    def __call__(self, b, h, w):
        mask = torch.zeros([b, h, w], dtype=torch.bool, device='cuda')
        assert mask is not None
        not_mask = ~mask
        y_embed = not_mask.cumsum(dim=1, dtype=torch.float32)
        x_embed = not_mask.cumsum(dim=2, dtype=torch.float32)
        if self.normalize:
            eps = 1e-6
            y_embed = ((y_embed - 0.5) / (y_embed[:, -1:, :] + eps) * self.scale).cuda()
            x_embed = ((x_embed - 0.5) / (x_embed[:, :, -1:] + eps) * self.scale).cuda()

        dim_t = self.temperature ** (2 * (self.dim_t // 2) / self.num_pos_feats)

        pos_x = x_embed[:, :, :, None] / dim_t
        pos_y = y_embed[:, :, :, None] / dim_t
        pos_x = torch.stack((pos_x[:, :, :, 0::2].sin(), pos_x[:, :, :, 1::2].cos()), dim=4).flatten(
            3)
        pos_y = torch.stack((pos_y[:, :, :, 0::2].sin(), pos_y[:, :, :, 1::2].cos()), dim=4).flatten(
            3)
        return torch.cat((pos_y, pos_x), dim=3).permute(0, 3, 1, 2)

class PCI(nn.Module):
    def __init__(self, in_channels, bias=True):  # 修改这里
        super(PCI, self).__init__()  # 注意这里也是 __init__
        
        self.unfold1 = nn.Unfold(kernel_size=(5,5), dilation=1, padding=2)

        self.ksz = [(1,1,1),(1,3,3),(1,5,5)]
        self.str = (1,1,1)
        self.pad = (0,0,0)
        self.num = 4
        self.unfold = nn.Unfold(kernel_size=(5,5),dilation=1, padding=2)
        self.conv3 = nn.Sequential(
            nn.Conv3d(in_channels, in_channels//self.num,self.ksz[1], self.str, self.pad, bias=bias),
            nn.BatchNorm3d(in_channels//self.num),
            nn.ReLU(inplace=True),
            nn.Conv3d(in_channels//self.num, in_channels,self.ksz[1], self.str, self.pad, bias=bias),
            nn.BatchNorm3d(in_channels),
            nn.ReLU(inplace=True)
        )
        self.conv5 = nn.Sequential(
            nn.Conv3d(in_channels, in_channels//self.num,self.ksz[2], self.str, self.pad, bias=bias),
            nn.BatchNorm3d(in_channels//self.num),
            nn.ReLU(inplace=True),
            nn.Conv3d(in_channels//self.num, in_channels,self.ksz[0], self.str, self.pad, bias=bias),
            nn.BatchNorm3d(in_channels),
            nn.ReLU(inplace=True)
        )


    def forward(self, x):

        b,c,h,w = x.shape

        x1 = self.unfold1(x) # b (5*5*c) (h w)
        x1 = rearrange(x1, 'b (c d e) (h w) -> b c (h w) d e', c=c, d=5, e=5, h=h, w=w)

        x1 = self.conv3(x1).mean([-1,-2]) * self.conv5(x1).mean([-1,-2])
        x1 = rearrange(x1, 'b c (h w) -> b c h w', h=h, w=w)

        out = x1 * x

        out = out + x

        out = out/2

        out = F.interpolate(out, size=(135, 240), mode='bilinear', align_corners=True)

        return out


class PLR(nn.Module):
    def __init__(self, in_channels):  # 修改这里
        super(PLR, self).__init__()  # 注意这里也是 __init__

        self.channels = in_channels

        self.linear1 = nn.ReLU(inplace=False)
        self.bn = nn.BatchNorm2d(in_channels)

        self.dwconv = _DWConv(in_channels, in_channels)

        self.positional_encoding = PositionEmbeddingSine(num_pos_feats=in_channels // 2, normalize=True)

    def forward(self, x):

        batch_size = x.size(0)
        batch_size_loc = int(batch_size/5*4)
        batch_size_glb = int(batch_size/5)

        loc, glb = x.split([batch_size_loc, batch_size_glb], dim=0)

        pos_emb_g = self.positional_encoding(glb.shape[0], glb.shape[2], glb.shape[3])
        pos_emb_l = self.positional_encoding(loc.shape[0], loc.shape[2], loc.shape[3])

        pos_emb_g = self.linear1(pos_emb_g)
        pos_emb_l = self.linear1(pos_emb_l)

        loc_all = loc + pos_emb_l
        glb_all = glb + pos_emb_g

        x_out = torch.cat([loc_all, glb_all], dim=0)

        x_out = self.dwconv(x_out)
        x_out = self.dwconv(x_out)

        x_out = x_out + x

        loc_out, glb_out = x_out.split([batch_size_loc, batch_size_glb], dim=0)

        return loc_out, glb_out


class MPK(nn.Module):
    def __init__(self, in_channels):  # 修改这里
        super(MPK, self).__init__()  # 注意这里也是 __init__

        self.dropout = nn.Dropout(0.1)

        self.PK = PositionKAN(in_channels)

        self.attention = nn.MultiheadAttention(in_channels, 1, dropout=0.1)


    def forward(self, x):

        glb = rescale_to(x, scale_factor=0.5, interpolation='bilinear')
        loc = image2patches(x)
        input = torch.cat([loc, glb], dim=0)

        loc, glb = self.PK(input)
        b1 = loc.size(0)
        c1 = loc.size(1)

        glb_4 = torch.cat([glb, glb, glb, glb], dim=0)

        # out = loc + self.dropout(self.attention(glb_4, loc, loc))

        k = rearrange(loc, 'b c h w -> b c (h w)')
        k = k.permute(0, 2, 1)
        v = rearrange(glb_4, 'b c h w -> b c (h w)')
        kv_matmul = torch.matmul(k, v)
        kv_matmul = F.softmax(kv_matmul, dim=-1)

        q = rearrange(loc, 'b c h w -> b c (h w)')
        kqv_matmul = torch.matmul(q, kv_matmul)
        out = kqv_matmul.view(b1, c1, *loc.size()[2:])

        out = out + loc

        out = patches2image(out)
        out = out + x

        # out = F.interpolate(out, size=(135, 240), mode='bilinear', align_corners=True)

        return out


class MPI(nn.Module):
    def __init__(self, in_channels, bias = True):  # 修改这里
        super(MPI, self).__init__()  # 注意这里也是 __init__

        self.pci = PCI(in_channels)
        self.mpk = MPK(in_channels)


    def forward(self, x):

        x = self.pci(x)

        x = self.mpk(x)

        x[x > 1] = 1

        x = F.relu(x,inplace=True)

        return x

if __name__ == '__main__':
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    args = 640
    d = MPI(3).to(device)
    b = torch.rand(16,3,84,84).to(device)
    out = d(b)