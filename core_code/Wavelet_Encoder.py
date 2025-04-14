from tokenize import Double

import torch
from monai.networks.blocks import UnetrBasicBlock
from thop import profile
from torch import nn
from torchinfo import summary

from models.AFEM import AFEM
from models.common import DWConv, Dwt2d, DoubleConv




# # 五层
# class Wavelet_Encoder(nn.Module):
#     def __init__(self, in_channels=1, embed_dim=96):
#         super().__init__()
#
#
#         self.dwt = Dwt2d()
#         self.conv2 = UnetrBasicBlock(
#             spatial_dims=2,
#             in_channels=embed_dim // 2,
#             out_channels=embed_dim // 2,
#             kernel_size=3,
#             stride=1,
#             norm_name="instance",
#             res_block=True,
#         )
#         self.conv3 = UnetrBasicBlock(
#             spatial_dims=2,
#             in_channels=embed_dim * 2,
#             out_channels=embed_dim,
#             kernel_size=3,
#             stride=1,
#             norm_name="instance",
#             res_block=True,
#         )
#         # self.afem3 = AFEM(embed_dim)
#         self.conv4 = UnetrBasicBlock(
#             spatial_dims=2,
#             in_channels=embed_dim * 4,
#             out_channels=embed_dim * 2,
#             kernel_size=3,
#             stride=1,
#             norm_name="instance",
#             res_block=True,
#         )
#         # self.afem4 = AFEM(embed_dim * 2)
#         self.conv5 = UnetrBasicBlock(
#             spatial_dims=2,
#             in_channels=embed_dim * 8,
#             out_channels=embed_dim * 4,
#             kernel_size=3,
#             stride=1,
#             norm_name="instance",
#             res_block=True,
#         )
#         # self.afem5 = AFEM(embed_dim * 4)
#         self.conv6 = UnetrBasicBlock(
#             spatial_dims=2,
#             in_channels=embed_dim * 16,
#             out_channels=embed_dim * 8,
#             kernel_size=3,
#             stride=1,
#             norm_name="instance",
#             res_block=True,
#         )
#         # self.afem6 = AFEM(embed_dim * 8)
#
#     def forward(self, x):
#         wx_list = []
#         # c1 = self.conv1(x)                           # 320
#         # w1 = self.dwt(c1, separate=False)           # 160
#         c1 = x
#         c2 = self.conv2(c1)
#         w2 = self.dwt(c2, separate=False)           # 80
#         c3 = self.conv3(w2)
#         # c3 = self.afem3(c3)
#         w3 = self.dwt(c3, separate=False)           # 40
#         c4 = self.conv4(w3)
#         # c4 = self.afem4(c4)
#         w4 = self.dwt(c4, separate=False)           # 20
#         c5 = self.conv5(w4)
#         # c5 = self.afem5(c5)
#         w5 = self.dwt(c5, separate=False)           # 10
#         c6 = self.conv6(w5)
#         # c6 = self.afem6(c6)
#
#         wx_list.extend([c1, c2, c3, c4, c5, c6])
#         return wx_list


# 五层
class Wavelet_Encoder(nn.Module):
    def __init__(self, in_channels=1, embed_dim=64):
        super().__init__()
        self.dwt = Dwt2d()

        self.conv1 = nn.Sequential(
            DoubleConv(in_channels, embed_dim // 4),
            # nn.Conv2d(in_channels, embed_dim // 4, 1),
            # nn.BatchNorm2d(embed_dim // 4),
            # nn.ReLU(inplace=True),
        )
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = nn.Sequential(
            DoubleConv(embed_dim // 4, embed_dim // 2),
            # nn.Conv2d(embed_dim, embed_dim // 2, 1),
            # nn.BatchNorm2d(embed_dim // 2),
            # nn.ReLU(inplace=True),
        )
        self.pool2 = nn.MaxPool2d(2)
        self.conv3 = nn.Sequential(
            DoubleConv(embed_dim // 2, embed_dim),
            # nn.Conv2d(embed_dim * 2, embed_dim, 1),
            # nn.BatchNorm2d(embed_dim),
            # nn.ReLU(inplace=True),
        )

        self.afem3 = AFEM(embed_dim)
        self.conv4 = nn.Sequential(
            # DoubleConv(embed_dim * 4, embed_dim * 2),
            nn.Conv2d(embed_dim * 4, embed_dim * 2, 1),
            nn.BatchNorm2d(embed_dim * 2),
            nn.ReLU(inplace=True),
        )
        # self.conv4 = DoubleConv(embed_dim * 4, embed_dim * 2)
        self.afem4 = AFEM(embed_dim * 2)
        self.conv5 = nn.Sequential(
            # DoubleConv(embed_dim * 8, embed_dim * 4),
            nn.Conv2d(embed_dim * 8, embed_dim * 4, 1),
            nn.BatchNorm2d(embed_dim * 4),
            nn.ReLU(inplace=True),
        )
        # self.conv5 = DoubleConv(embed_dim * 8, embed_dim * 4)
        self.afem5 = AFEM(embed_dim * 4)
        self.conv6 = nn.Sequential(
            # DoubleConv(embed_dim * 8, embed_dim * 4),
            nn.Conv2d(embed_dim * 16, embed_dim * 8, 1),
            nn.BatchNorm2d(embed_dim * 8),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        wx_list = []
        c1 = self.conv1(x)                           # 320
        w1 = self.pool1(c1)                        # 160
        # w1 = self.dwt(c1, separate=False)
        c2 = self.conv2(w1)
        w2 = self.pool2(c2)                        # 80
        # w2 = self.dwt(c2, separate=False)
        c3 = self.conv3(w2)
        c3 = self.afem3(c3)
        w3 = self.dwt(c3, separate=False)           # 40
        c4 = self.conv4(w3)
        c4 = self.afem4(c4)
        w4 = self.dwt(c4, separate=False)           # 20
        c5 = self.conv5(w4)
        c5 = self.afem5(c5)
        w5 = self.dwt(c5, separate=False)           # 20
        c6 = self.conv6(w5)

        wx_list.extend([c1, c2, c3, c4, c5, c6])
        return c6, wx_list


# # 四层
# class Wavelet_Encoder(nn.Module):
#     def __init__(self, in_channels=1, embed_dim=96):
#         super().__init__()
#
#         self.conv1 = DoubleConv(in_channels, embed_dim // 4)
#         self.dwt1 = Dwt2d()
#         self.conv2 = nn.Conv2d(embed_dim, embed_dim // 2, 1)
#         self.dwt2 = Dwt2d()
#         self.afem3 = AFEM(embed_dim * 2)
#         self.conv3 = nn.Conv2d(embed_dim * 2, embed_dim, 1)
#         self.dwt3 = Dwt2d()
#         self.afem4 = AFEM(embed_dim * 4)
#         self.conv4 = nn.Conv2d(embed_dim * 4, embed_dim * 2, 1)
#
#
#     def forward(self, x):
#         wx_list = []
#         c1 = self.conv1(x)           # 320
#         w1 = self.dwt1(c1, separate=False)           # 160
#         c2 = self.conv2(w1)
#         w2 = self.dwt2(c2, separate=False)           # 80
#         w2 = self.afem3(w2)
#         c3 = self.conv3(w2)
#         w3 = self.dwt3(c3, separate=False)           # 40
#         w3 = self.afem4(w3)
#         c4 = self.conv4(w3)
#
#         wx_list.extend([c1, c2, c3, c4])
#         return wx_list


# # 四层
# class Wavelet_Encoder(nn.Module):
#     def __init__(self, in_channels=1, embed_dim=96):
#         super().__init__()
#
#         self.conv1 = DWConv(in_channels, embed_dim // 4)
#         self.dwt1 = Dwt2d()
#         self.conv2 = nn.Conv2d(embed_dim, embed_dim // 2, 1)
#         self.dwt2 = Dwt2d()
#         self.afem3 = AFEM(embed_dim * 2)
#         self.conv3 = nn.Conv2d(embed_dim * 2, embed_dim, 1)
#         self.dwt3 = Dwt2d()
#         self.afem4 = AFEM(embed_dim * 4)
#         self.conv4 = nn.Conv2d(embed_dim * 4, embed_dim * 2, 1)
#
#
#     def forward(self, x):
#         wx_list = []
#         c1 = self.conv1(x)           # 320
#         w1 = self.dwt1(c1, separate=False)           # 160
#         c2 = self.conv2(w1)
#         w2 = self.dwt2(c2, separate=False)           # 80
#         w2 = self.afem3(w2)
#         c3 = self.conv3(w2)
#         w3 = self.dwt3(c3, separate=False)           # 40
#         w3 = self.afem4(w3)
#         c4 = self.conv4(w3)
#
#         wx_list.extend([c1, c2, c3, c4])
#         return wx_list





if __name__ == '__main__':
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    net = Wavelet_Encoder(in_channels=1).to(device)
    # 打印网络结构和参数
    summary(net, (2, 1, 320, 320))

if __name__ == "__main__":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    net = Wavelet_Encoder(in_channels=1).to(device)
    inputs = torch.randn(1, 1, 320, 320).to(device)
    flops, params = profile(net, (inputs,))
    print("FLOPs=, params=", flops, params)
    print("FLOPs=", str(flops / 1e9) + '{}'.format("G"))
    print("params=", str(params / 1e6) + '{}'.format("M"))

    import time
    import numpy as np


    def calculate_fps(model, input_size, batch_size=1, num_iterations=100):
        t_all = []
        # 模型设置为评估模式
        model.eval()
        # 模拟输入数据
        input_data = torch.randn(batch_size, *input_size).to(device)  # 如果有GPU的话

        # 运行推理多次
        with torch.no_grad():
            for _ in range(num_iterations):
                # 启动计时器
                start_time = time.time()
                output = model(input_data)
                # 计算总时间
                total_time = time.time() - start_time
                t_all.append(total_time)

        print('average time:', np.mean(t_all) / 1)
        print('average fps:', 1 / np.mean(t_all))

        print('fastest time:', min(t_all) / 1)
        print('fastest fps:', 1 / min(t_all))

        print('slowest time:', max(t_all) / 1)
        print('slowest fps:', 1 / max(t_all))


    calculate_fps(net, input_size=(1, 320, 320), batch_size=2, num_iterations=10)





# # 四层
# class Wavelet_Encoder(nn.Module):
#     def __init__(self, in_channels=1, embed_dim=96):
#         super().__init__()
#
#         self.conv1 = DoubleConv(in_channels, embed_dim // 4)
#         self.pool1 = nn.MaxPool2d(2)
#         self.conv2 = DoubleConv(embed_dim // 4, embed_dim // 2)
#         self.pool2 = nn.MaxPool2d(2)
#         self.conv3 = DoubleConv(embed_dim // 2, embed_dim)
#         # self.afem3 = AFEM(embed_dim)
#         self.dwt3 = Dwt2d()
#         self.conv4 = nn.Sequential(
#             # DoubleConv(embed_dim * 4, embed_dim * 2),
#             nn.Conv2d(embed_dim * 4, embed_dim * 2, 1),
#             nn.BatchNorm2d(embed_dim * 2),
#             nn.ReLU(inplace=True),
#         )
#         # self.conv4 = DoubleConv(embed_dim * 4, embed_dim * 2)
#         self.afem4 = AFEM(embed_dim * 2)
#
#     def forward(self, x):
#         wx_list = []
#         c1 = self.conv1(x)                           # 320
#         w1 = self.pool1(c1)                          # 160
#         c2 = self.conv2(w1)
#         w2 = self.pool2(c2)                          # 80
#         c3 = self.conv3(w2)
#         # c3 = self.afem3(c3)
#         w3 = self.dwt3(c3, separate=False)           # 40
#         c4 = self.conv4(w3)
#         c4 = self.afem4(c4)
#
#         wx_list.extend([c1, c2, c3, c4])
#         return wx_list


# # 四层
# class Wavelet_Encoder(nn.Module):
#     def __init__(self, in_channels=1, embed_dim=96):
#         super().__init__()
#
#         self.conv1 = DoubleConv(in_channels, embed_dim // 4)
#         self.pool1 = nn.MaxPool2d(2)
#         self.conv2 = DoubleConv(embed_dim // 4, embed_dim // 2)
#         self.pool2 = nn.MaxPool2d(2)
#         # self.dwt2 = Dwt2d()
#         self.conv3 = DoubleConv(embed_dim // 2, embed_dim)
#         self.afem3 = AFEM(embed_dim)
#         self.dwt3 = Dwt2d()
#         self.conv4 = nn.Sequential(
#             # DoubleConv(embed_dim * 4, embed_dim * 2),
#             nn.Conv2d(embed_dim * 4, embed_dim * 2, 1),
#             nn.BatchNorm2d(embed_dim * 2),
#             nn.ReLU(inplace=True),
#         )
#         self.afem4 = AFEM(embed_dim * 2)
#
#     def forward(self, x):
#         wx_list = []
#         c1 = self.conv1(x)                           # 320
#         w1 = self.pool1(c1)                          # 160
#         c2 = self.conv2(w1)
#         w2 = self.pool2(c2)                          # 80
#         c3 = self.conv3(w2)
#         c3 = self.afem3(c3)
#         w3 = self.dwt3(c3, separate=False)           # 40
#         c4 = self.conv4(w3)
#         c4 = self.afem4(c4)
#
#         wx_list.extend([c1, c2, c3, c4])
#         return wx_list

