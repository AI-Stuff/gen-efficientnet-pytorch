""" Generic Efficient Networks

A generic MobileNet class with building blocks to support a variety of models:
* EfficientNet (B0-B5 + Tensorflow pretrained ports)
* MixNet (Small, Medium, and Large)
* MNasNet B1, A1 (SE), Small
* MobileNet V3
* FBNet-C (TODO A & B)
* ChamNet (TODO still guessing at architecture definition)
* Single-Path NAS Pixel1
* And likely more...

Hacked together by Ross Wightman
"""

import math

import torch.nn as nn
import torch.nn.functional as F

from .helpers import load_state_dict_from_url
from .layers import Flatten
from .efficientnet_builder import *

__all__ = ['GenEfficientNet', 'mnasnet_050', 'mnasnet_075', 'mnasnet_100', 'mnasnet_b1', 'mnasnet_140',
           'semnasnet_050', 'semnasnet_075', 'semnasnet_100', 'mnasnet_a1', 'semnasnet_140',
           'mnasnet_small', 'chamnetv1_100', 'chamnetv2_100', 'fbnetc_100', 'spnasnet_100', 'efficientnet_b0',
           'efficientnet_b1', 'efficientnet_b2', 'efficientnet_b3', 'efficientnet_b4', 'efficientnet_b5',
           'efficientnet_es', 'efficientnet_em', 'efficientnet_el',
           'tf_efficientnet_b0', 'tf_efficientnet_b1', 'tf_efficientnet_b2', 'tf_efficientnet_b3',
           'tf_efficientnet_b4', 'tf_efficientnet_b5', 'tf_efficientnet_b6', 'tf_efficientnet_b7',
           'tf_efficientnet_es', 'tf_efficientnet_em', 'tf_efficientnet_el',
           'tf_efficientnet_cc_b0_4e', 'tf_efficientnet_cc_b0_8e', 'tf_efficientnet_cc_b1_8e',
           'mixnet_s', 'mixnet_m', 'mixnet_l', 'mixnet_xl', 'tf_mixnet_s', 'tf_mixnet_m', 'tf_mixnet_l']


model_urls = {
    'mnasnet_050': None,
    'mnasnet_075': None,
    'mnasnet_100':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mnasnet_b1-74cb7081.pth',
    'mnasnet_140': None,
    'semnasnet_050': None,
    'semnasnet_075': None,
    'semnasnet_100':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mnasnet_a1-d9418771.pth',
    'semnasnet_140': None,
    'mnasnet_small': None,
    'fbnetc_100':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/fbnetc_100-c345b898.pth',
    'spnasnet_100':
        'https://www.dropbox.com/s/iieopt18rytkgaa/spnasnet_100-048bc3f4.pth?dl=1',
    'efficientnet_b0':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_b0-d6904d92.pth',
    'efficientnet_b1':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_b1-533bc792.pth',
    'efficientnet_b2':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/efficientnet_b2-cf78dc4d.pth',
    'efficientnet_b3': None,
    'efficientnet_b4': None,
    'efficientnet_b5': None,
    'efficientnet_es': None,
    'efficientnet_em': None,
    'efficientnet_el': None,
    'tf_efficientnet_b0':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b0_aa-827b6e33.pth',
    'tf_efficientnet_b1':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b1_aa-ea7a6ee0.pth',
    'tf_efficientnet_b2':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b2_aa-60c94f97.pth',
    'tf_efficientnet_b3':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b3_aa-84b4657e.pth',
    'tf_efficientnet_b4':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b4_aa-818f208c.pth',
    'tf_efficientnet_b5':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b5_ra-9a3e5369.pth',
    'tf_efficientnet_b6':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b6_aa-80ba17e4.pth',
    'tf_efficientnet_b7':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_b7_ra-6c08e654.pth',
    'tf_efficientnet_es':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_es-ca1afbfe.pth',
    'tf_efficientnet_em':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_em-e78cfe58.pth',
    'tf_efficientnet_el':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_el-5143854e.pth',
    'tf_efficientnet_cc_b0_4e':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_cc_b0_4e-4362b6b2.pth',
    'tf_efficientnet_cc_b0_8e':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_cc_b0_8e-66184a25.pth',
    'tf_efficientnet_cc_b1_8e':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_efficientnet_cc_b1_8e-f7c79ae1.pth',
    'mixnet_s': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mixnet_s-a907afbc.pth',
    'mixnet_m': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mixnet_m-4647fc68.pth',
    'mixnet_l': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mixnet_l-5a9a2ed8.pth',
    'mixnet_xl': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/mixnet_xl-ac5fbe8d.pth',
    'tf_mixnet_s':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_mixnet_s-89d3354b.pth',
    'tf_mixnet_m':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_mixnet_m-0f4d8805.pth',
    'tf_mixnet_l':
        'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/tf_mixnet_l-6c92e0c8.pth',
}


class GenEfficientNet(nn.Module):
    """ Generic Efficient Networks

    An implementation of mobile optimized networks that covers:
      * EfficientNet (B0-B5)
      * MixNet (Small, Medium, and Large)
      * MNASNet A1, B1, and small
      * FBNet C
      * Single-Path NAS Pixel1
    """

    def __init__(self, block_args, num_classes=1000, in_chans=3, stem_size=32, num_features=1280,
                 channel_multiplier=1.0, channel_divisor=8, channel_min=None,
                 pad_type='', act_layer=nn.ReLU, drop_rate=0., drop_connect_rate=0.,
                 se_gate_fn=sigmoid, se_reduce_mid=False, bn_args=BN_ARGS_PT, weight_init='goog'):
        super(GenEfficientNet, self).__init__()
        self.drop_rate = drop_rate

        stem_size = round_channels(stem_size, channel_multiplier, channel_divisor, channel_min)
        self.conv_stem = select_conv2d(in_chans, stem_size, 3, stride=2, padding=pad_type)
        self.bn1 = nn.BatchNorm2d(stem_size, **bn_args)
        self.act1 = act_layer(inplace=True)
        in_chs = stem_size

        builder = EfficientNetBuilder(
            channel_multiplier, channel_divisor, channel_min,
            pad_type, act_layer, se_gate_fn, se_reduce_mid,
            bn_args, drop_connect_rate)
        self.blocks = nn.Sequential(*builder(in_chs, block_args))
        in_chs = builder.in_chs

        self.conv_head = select_conv2d(in_chs, num_features, 1, padding=pad_type)
        self.bn2 = nn.BatchNorm2d(num_features, **bn_args)
        self.act2 = act_layer(inplace=True)
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Linear(num_features, num_classes)

        for m in self.modules():
            if weight_init == 'goog':
                initialize_weight_goog(m)
            else:
                initialize_weight_default(m)

    def features(self, x):
        x = self.conv_stem(x)
        x = self.bn1(x)
        x = self.act1(x)
        x = self.blocks(x)
        x = self.conv_head(x)
        x = self.bn2(x)
        x = self.act2(x)
        x = self.global_pool(x)
        return x

    def as_sequential(self):
        layers = [self.conv_stem, self.bn1, self.act1]
        layers.extend(self.blocks)
        layers.extend([
            self.conv_head, self.bn2, self.act2,
            self.global_pool, Flatten(), nn.Dropout(self.drop_rate), self.classifier])
        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.features(x)
        x = x.flatten(1)
        if self.drop_rate > 0.:
            x = F.dropout(x, p=self.drop_rate, training=self.training)
        return self.classifier(x)


def _gen_mnasnet_a1(channel_multiplier, num_classes=1000, **kwargs):
    """Creates a mnasnet-a1 model.

    Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet
    Paper: https://arxiv.org/pdf/1807.11626.pdf.

    Args:
      channel_multiplier: multiplier to number of channels per layer.
    """
    arch_def = [
        # stage 0, 112x112 in
        ['ds_r1_k3_s1_e1_c16_noskip'],
        # stage 1, 112x112 in
        ['ir_r2_k3_s2_e6_c24'],
        # stage 2, 56x56 in
        ['ir_r3_k5_s2_e3_c40_se0.25'],
        # stage 3, 28x28 in
        ['ir_r4_k3_s2_e6_c80'],
        # stage 4, 14x14in
        ['ir_r2_k3_s1_e6_c112_se0.25'],
        # stage 5, 14x14in
        ['ir_r3_k5_s2_e6_c160_se0.25'],
        # stage 6, 7x7 in
        ['ir_r1_k3_s1_e6_c320'],
    ]
    model = GenEfficientNet(
        decode_arch_def(arch_def),
        num_classes=num_classes,
        stem_size=32,
        channel_multiplier=channel_multiplier,
        channel_divisor=8,
        channel_min=None,
        bn_args=resolve_bn_args(kwargs),
        **kwargs
    )
    return model


def _gen_mnasnet_b1(channel_multiplier, num_classes=1000, **kwargs):
    """Creates a mnasnet-b1 model.

    Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet
    Paper: https://arxiv.org/pdf/1807.11626.pdf.

    Args:
      channel_multiplier: multiplier to number of channels per layer.
    """
    arch_def = [
        # stage 0, 112x112 in
        ['ds_r1_k3_s1_c16_noskip'],
        # stage 1, 112x112 in
        ['ir_r3_k3_s2_e3_c24'],
        # stage 2, 56x56 in
        ['ir_r3_k5_s2_e3_c40'],
        # stage 3, 28x28 in
        ['ir_r3_k5_s2_e6_c80'],
        # stage 4, 14x14in
        ['ir_r2_k3_s1_e6_c96'],
        # stage 5, 14x14in
        ['ir_r4_k5_s2_e6_c192'],
        # stage 6, 7x7 in
        ['ir_r1_k3_s1_e6_c320_noskip']
    ]
    model = GenEfficientNet(
        decode_arch_def(arch_def),
        num_classes=num_classes,
        stem_size=32,
        channel_multiplier=channel_multiplier,
        channel_divisor=8,
        channel_min=None,
        bn_args=resolve_bn_args(kwargs),
        **kwargs
    )
    return model


def _gen_mnasnet_small(channel_multiplier, num_classes=1000, **kwargs):
    """Creates a mnasnet-b1 model.

    Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet
    Paper: https://arxiv.org/pdf/1807.11626.pdf.

    Args:
      channel_multiplier: multiplier to number of channels per layer.
    """
    arch_def = [
        ['ds_r1_k3_s1_c8'],
        ['ir_r1_k3_s2_e3_c16'],
        ['ir_r2_k3_s2_e6_c16'],
        ['ir_r4_k5_s2_e6_c32_se0.25'],
        ['ir_r3_k3_s1_e6_c32_se0.25'],
        ['ir_r3_k5_s2_e6_c88_se0.25'],
        ['ir_r1_k3_s1_e6_c144']
    ]
    model = GenEfficientNet(
        decode_arch_def(arch_def),
        num_classes=num_classes,
        stem_size=8,
        channel_multiplier=channel_multiplier,
        channel_divisor=8,
        channel_min=None,
        bn_args=resolve_bn_args(kwargs),
        **kwargs
    )
    return model


def _gen_fbnetc(channel_multiplier, num_classes=1000, **kwargs):
    """ FBNet-C

        Paper: https://arxiv.org/abs/1812.03443
        Ref Impl: https://github.com/facebookresearch/maskrcnn-benchmark/blob/master/maskrcnn_benchmark/modeling/backbone/fbnet_modeldef.py

        NOTE: the impl above does not relate to the 'C' variant here, that was derived from paper,
        it was used to confirm some building block details
    """
    arch_def = [
        ['ir_r1_k3_s1_e1_c16'],
        ['ir_r1_k3_s2_e6_c24', 'ir_r2_k3_s1_e1_c24'],
        ['ir_r1_k5_s2_e6_c32', 'ir_r1_k5_s1_e3_c32', 'ir_r1_k5_s1_e6_c32', 'ir_r1_k3_s1_e6_c32'],
        ['ir_r1_k5_s2_e6_c64', 'ir_r1_k5_s1_e3_c64', 'ir_r2_k5_s1_e6_c64'],
        ['ir_r3_k5_s1_e6_c112', 'ir_r1_k5_s1_e3_c112'],
        ['ir_r4_k5_s2_e6_c184'],
        ['ir_r1_k3_s1_e6_c352'],
    ]
    model = GenEfficientNet(
        decode_arch_def(arch_def),
        num_classes=num_classes,
        stem_size=16,
        num_features=1984,  # paper suggests this, but is not 100% clear
        channel_multiplier=channel_multiplier,
        channel_divisor=8,
        channel_min=None,
        bn_args=resolve_bn_args(kwargs),
        **kwargs
    )
    return model


def _gen_spnasnet(channel_multiplier, num_classes=1000, **kwargs):
    """Creates the Single-Path NAS model from search targeted for Pixel1 phone.

    Paper: https://arxiv.org/abs/1904.02877

    Args:
      channel_multiplier: multiplier to number of channels per layer.
    """
    arch_def = [
        # stage 0, 112x112 in
        ['ds_r1_k3_s1_c16_noskip'],
        # stage 1, 112x112 in
        ['ir_r3_k3_s2_e3_c24'],
        # stage 2, 56x56 in
        ['ir_r1_k5_s2_e6_c40', 'ir_r3_k3_s1_e3_c40'],
        # stage 3, 28x28 in
        ['ir_r1_k5_s2_e6_c80', 'ir_r3_k3_s1_e3_c80'],
        # stage 4, 14x14in
        ['ir_r1_k5_s1_e6_c96', 'ir_r3_k5_s1_e3_c96'],
        # stage 5, 14x14in
        ['ir_r4_k5_s2_e6_c192'],
        # stage 6, 7x7 in
        ['ir_r1_k3_s1_e6_c320_noskip']
    ]
    model = GenEfficientNet(
        decode_arch_def(arch_def),
        num_classes=num_classes,
        stem_size=32,
        channel_multiplier=channel_multiplier,
        channel_divisor=8,
        channel_min=None,
        bn_args=resolve_bn_args(kwargs),
        **kwargs
    )
    return model


def _gen_efficientnet(channel_multiplier=1.0, depth_multiplier=1.0, num_classes=1000, **kwargs):
    """Creates an EfficientNet model.

    Ref impl: https://github.com/tensorflow/tpu/blob/master/models/official/efficientnet/efficientnet_model.py
    Paper: https://arxiv.org/abs/1905.11946

    EfficientNet params
    name: (channel_multiplier, depth_multiplier, resolution, dropout_rate)
    'efficientnet-b0': (1.0, 1.0, 224, 0.2),
    'efficientnet-b1': (1.0, 1.1, 240, 0.2),
    'efficientnet-b2': (1.1, 1.2, 260, 0.3),
    'efficientnet-b3': (1.2, 1.4, 300, 0.3),
    'efficientnet-b4': (1.4, 1.8, 380, 0.4),
    'efficientnet-b5': (1.6, 2.2, 456, 0.4),
    'efficientnet-b6': (1.8, 2.6, 528, 0.5),
    'efficientnet-b7': (2.0, 3.1, 600, 0.5),

    Args:
      channel_multiplier: multiplier to number of channels per layer
      depth_multiplier: multiplier to number of repeats per stage

    """
    arch_def = [
        ['ds_r1_k3_s1_e1_c16_se0.25'],
        ['ir_r2_k3_s2_e6_c24_se0.25'],
        ['ir_r2_k5_s2_e6_c40_se0.25'],
        ['ir_r3_k3_s2_e6_c80_se0.25'],
        ['ir_r3_k5_s1_e6_c112_se0.25'],
        ['ir_r4_k5_s2_e6_c192_se0.25'],
        ['ir_r1_k3_s1_e6_c320_se0.25'],
    ]
    model = GenEfficientNet(
        decode_arch_def(arch_def, depth_multiplier),
        num_classes=num_classes,
        stem_size=32,
        channel_multiplier=channel_multiplier,
        channel_divisor=8,
        channel_min=None,
        num_features=round_channels(1280, channel_multiplier, 8, None),
        bn_args=resolve_bn_args(kwargs),
        act_layer=Swish,
        **kwargs
    )
    return model


def _gen_efficientnet_edge(channel_multiplier=1.0, depth_multiplier=1.0, num_classes=1000, **kwargs):
    arch_def = [
        # NOTE `fc` is present to override a mismatch between stem channels and in chs not
        # present in other models
        ['er_r1_k3_s1_e4_c24_fc24_noskip'],
        ['er_r2_k3_s2_e8_c32'],
        ['er_r4_k3_s2_e8_c48'],
        ['ir_r5_k5_s2_e8_c96'],
        ['ir_r4_k5_s1_e8_c144'],
        ['ir_r2_k5_s2_e8_c192'],
    ]
    num_features = round_channels(1280, channel_multiplier, 8, None)
    model = GenEfficientNet(
        decode_arch_def(arch_def, depth_multiplier),
        num_classes=num_classes,
        stem_size=32,
        channel_multiplier=channel_multiplier,
        num_features=num_features,
        bn_args=resolve_bn_args(kwargs),
        act_layer=nn.ReLU,
        **kwargs
    )
    return model


def _gen_efficientnet_condconv(
        channel_multiplier=1.0, depth_multiplier=1.0, experts_multiplier=1, num_classes=1000, **kwargs):

    """Creates an efficientnet-condconv model."""
    arch_def = [
      ['ds_r1_k3_s1_e1_c16_se0.25'],
      ['ir_r2_k3_s2_e6_c24_se0.25'],
      ['ir_r2_k5_s2_e6_c40_se0.25'],
      ['ir_r3_k3_s2_e6_c80_se0.25'],
      ['ir_r3_k5_s1_e6_c112_se0.25_cc4'],
      ['ir_r4_k5_s2_e6_c192_se0.25_cc4'],
      ['ir_r1_k3_s1_e6_c320_se0.25_cc4'],
    ]
    model = GenEfficientNet(
        decode_arch_def(arch_def, depth_multiplier, experts_multiplier=experts_multiplier),
        num_classes=num_classes,
        stem_size=32,
        channel_multiplier=channel_multiplier,
        channel_divisor=8,
        channel_min=None,
        num_features=round_channels(1280, channel_multiplier, 8, None),
        bn_args=resolve_bn_args(kwargs),
        act_layer=Swish,
        **kwargs
    )
    return model


def _gen_mixnet_s(channel_multiplier=1.0, num_classes=1000, **kwargs):
    """Creates a MixNet Small model.

    Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet/mixnet
    Paper: https://arxiv.org/abs/1907.09595
    """
    arch_def = [
        # stage 0, 112x112 in
        ['ds_r1_k3_s1_e1_c16'],  # relu
        # stage 1, 112x112 in
        ['ir_r1_k3_a1.1_p1.1_s2_e6_c24', 'ir_r1_k3_a1.1_p1.1_s1_e3_c24'],  # relu
        # stage 2, 56x56 in
        ['ir_r1_k3.5.7_s2_e6_c40_se0.5_nsw', 'ir_r3_k3.5_a1.1_p1.1_s1_e6_c40_se0.5_nsw'],  # swish
        # stage 3, 28x28 in
        ['ir_r1_k3.5.7_p1.1_s2_e6_c80_se0.25_nsw', 'ir_r2_k3.5_p1.1_s1_e6_c80_se0.25_nsw'],  # swish
        # stage 4, 14x14in
        ['ir_r1_k3.5.7_a1.1_p1.1_s1_e6_c120_se0.5_nsw', 'ir_r2_k3.5.7.9_a1.1_p1.1_s1_e3_c120_se0.5_nsw'],  # swish
        # stage 5, 14x14in
        ['ir_r1_k3.5.7.9.11_s2_e6_c200_se0.5_nsw', 'ir_r2_k3.5.7.9_p1.1_s1_e6_c200_se0.5_nsw'],  # swish
        # 7x7
    ]
    model = GenEfficientNet(
        decode_arch_def(arch_def),
        num_classes=num_classes,
        stem_size=16,
        num_features=1536,
        channel_multiplier=channel_multiplier,
        channel_divisor=8,
        channel_min=None,
        bn_args=resolve_bn_args(kwargs),
        act_layer=nn.ReLU,
        **kwargs
    )
    return model


def _gen_mixnet_m(channel_multiplier=1.0, depth_multiplier=1.0, num_classes=1000, **kwargs):
    """Creates a MixNet Medium-Large model.

    Ref impl: https://github.com/tensorflow/tpu/tree/master/models/official/mnasnet/mixnet
    Paper: https://arxiv.org/abs/1907.09595
    """
    arch_def = [
        # stage 0, 112x112 in
        ['ds_r1_k3_s1_e1_c24'],  # relu
        # stage 1, 112x112 in
        ['ir_r1_k3.5.7_a1.1_p1.1_s2_e6_c32', 'ir_r1_k3_a1.1_p1.1_s1_e3_c32'],  # relu
        # stage 2, 56x56 in
        ['ir_r1_k3.5.7.9_s2_e6_c40_se0.5_nsw', 'ir_r3_k3.5_a1.1_p1.1_s1_e6_c40_se0.5_nsw'],  # swish
        # stage 3, 28x28 in
        ['ir_r1_k3.5.7_s2_e6_c80_se0.25_nsw', 'ir_r3_k3.5.7.9_a1.1_p1.1_s1_e6_c80_se0.25_nsw'],  # swish
        # stage 4, 14x14in
        ['ir_r1_k3_s1_e6_c120_se0.5_nsw', 'ir_r3_k3.5.7.9_a1.1_p1.1_s1_e3_c120_se0.5_nsw'],  # swish
        # stage 5, 14x14in
        ['ir_r1_k3.5.7.9_s2_e6_c200_se0.5_nsw', 'ir_r3_k3.5.7.9_p1.1_s1_e6_c200_se0.5_nsw'],  # swish
        # 7x7
    ]
    model = GenEfficientNet(
        decode_arch_def(arch_def, depth_multiplier=depth_multiplier, depth_trunc='round'),
        num_classes=num_classes,
        stem_size=24,
        num_features=1536,
        channel_multiplier=channel_multiplier,
        channel_divisor=8,
        channel_min=None,
        bn_args=resolve_bn_args(kwargs),
        act_layer=nn.ReLU,
        **kwargs
    )
    return model


def mnasnet_050(pretrained=False, **kwargs):
    """ MNASNet B1, depth multiplier of 0.5. """
    model = _gen_mnasnet_b1(0.5, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['mnasnet_050']))
    return model


def mnasnet_075(pretrained=False, **kwargs):
    """ MNASNet B1, depth multiplier of 0.75. """
    model = _gen_mnasnet_b1(0.75, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['mnasnet_075']))
    return model


def mnasnet_100(pretrained=False, **kwargs):
    """ MNASNet B1, depth multiplier of 1.0. """
    model = _gen_mnasnet_b1(1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['mnasnet_100']))
    return model


def mnasnet_b1(pretrained=False, **kwargs):
    """ MNASNet B1, depth multiplier of 1.0.

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet-1K
    """
    return mnasnet_100(pretrained, **kwargs)


def mnasnet_140(pretrained=False, **kwargs):
    """ MNASNet B1,  depth multiplier of 1.4 """
    model = _gen_mnasnet_b1(1.4, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['mnasnet_140']))
    return model


def semnasnet_050(pretrained=False, **kwargs):
    """ MNASNet A1 (w/ SE), depth multiplier of 0.5 """
    model = _gen_mnasnet_a1(0.5, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['semnasnet_050']))
    return model


def semnasnet_075(pretrained=False, **kwargs):
    """ MNASNet A1 (w/ SE),  depth multiplier of 0.75. """
    model = _gen_mnasnet_a1(0.75, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['semnasnet_075']))
    return model


def semnasnet_100(pretrained=False, **kwargs):
    """ MNASNet A1 (w/ SE), depth multiplier of 1.0

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet-1K
    """
    model = _gen_mnasnet_a1(1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['semnasnet_100']))
    return model


def mnasnet_a1(pretrained=False, **kwargs):
    """ MNASNet A1 (w/ SE), depth multiplier of 1.0

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet-1K
    """
    return semnasnet_100(pretrained, **kwargs)


def semnasnet_140(pretrained=False, **kwargs):
    """ MNASNet A1 (w/ SE), depth multiplier of 1.4. """
    model = _gen_mnasnet_a1(1.4, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['semnasnet_140']))
    return model


def mnasnet_small(pretrained=False, **kwargs):
    """ MNASNet Small,  depth multiplier of 1.0. """
    model = _gen_mnasnet_small(1.0, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['mnasnet_small']))
    return model


def fbnetc_100(pretrained=False, **kwargs):
    """ FBNet-C 100 (depth_multiplier == 1.0) model

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet-1K

    """
    if pretrained and 'bn_eps' not in kwargs:
        # pretrained model trained with non-default BN epsilon
        kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    model = _gen_fbnetc(1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['fbnetc_100']))
    return model


def chamnetv1_100(pretrained=False, **kwargs):
    """ ChamNet """
    model = _gen_chamnet_v1(1.0, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['chamnetv1_100']))
    return model


def chamnetv2_100(pretrained=False, **kwargs):
    """ ChamNet """
    model = _gen_chamnet_v2(1.0, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['chamnetv2_100']))
    return model


def spnasnet_100(pretrained=False, **kwargs):
    """ Single-Path NAS Pixel1"""
    model = _gen_spnasnet(1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['spnasnet_100']))
    return model


def efficientnet_b0(pretrained=False, **kwargs):
    """ EfficientNet-B0 model

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet-1K
    """
    model = _gen_efficientnet(channel_multiplier=1.0, depth_multiplier=1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['efficientnet_b0']))
    return model


def efficientnet_b1(pretrained=False, **kwargs):
    """ EfficientNet-B1 """
    model = _gen_efficientnet(channel_multiplier=1.0, depth_multiplier=1.1, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['efficientnet_b1']))
    return model


def efficientnet_b2(pretrained=False, **kwargs):
    """ EfficientNet-B2 """
    model = _gen_efficientnet(channel_multiplier=1.1, depth_multiplier=1.2, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['efficientnet_b2']))
    return model


def efficientnet_b3(pretrained=False, **kwargs):
    """ EfficientNet-B3 """
    # NOTE for train, drop_rate should be 0.3
    model = _gen_efficientnet(channel_multiplier=1.2, depth_multiplier=1.4, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['efficientnet_b3']))
    return model


def efficientnet_b4(pretrained=False, **kwargs):
    """ EfficientNet-B4 """
    model = _gen_efficientnet(channel_multiplier=1.4, depth_multiplier=1.8, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['efficientnet_b4']))
    return model


def efficientnet_b5(pretrained=False, **kwargs):
    """ EfficientNet-B4 """
    model = _gen_efficientnet(channel_multiplier=1.6, depth_multiplier=2.2, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['efficientnet_b4']))
    return model


def efficientnet_es(pretrained=False, **kwargs):
    """ EfficientNet-Edge Small. """
    model = _gen_efficientnet_edge(channel_multiplier=1.0, depth_multiplier=1.0, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['efficientnet_es']))
    return model


def efficientnet_em(pretrained=False, **kwargs):
    """ EfficientNet-Edge-Medium. """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet_edge(channel_multiplier=1.0, depth_multiplier=1.1, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['efficientnet_em']))
    return model


def efficientnet_el(pretrained=False, **kwargs):
    """ EfficientNet-Edge-Large. Tensorflow compatible variant  """
    model = _gen_efficientnet_edge(channel_multiplier=1.2, depth_multiplier=1.4, **kwargs)
    #if pretrained:
    #    model.load_state_dict(load_state_dict_from_url(model_urls['efficientnet_el']))
    return model


def tf_efficientnet_b0(pretrained=False, **kwargs):
    """ EfficientNet-B0. Tensorflow compatible variant  """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet(channel_multiplier=1.0, depth_multiplier=1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_b0']))
    return model


def tf_efficientnet_b1(pretrained=False, **kwargs):
    """ EfficientNet-B1. Tensorflow compatible variant  """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet(channel_multiplier=1.0, depth_multiplier=1.1, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_b1']))
    return model


def tf_efficientnet_b2(pretrained=False, **kwargs):
    """ EfficientNet-B2. Tensorflow compatible variant  """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet(channel_multiplier=1.1, depth_multiplier=1.2, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_b2']))
    return model


def tf_efficientnet_b3(pretrained=False, **kwargs):
    """ EfficientNet-B3. Tensorflow compatible variant """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet(channel_multiplier=1.2, depth_multiplier=1.4, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_b3']))
    return model


def tf_efficientnet_b4(pretrained=False, **kwargs):
    """ EfficientNet-B4. Tensorflow compatible variant """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet(channel_multiplier=1.4, depth_multiplier=1.8, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_b4']))
    return model


def tf_efficientnet_b5(pretrained=False, **kwargs):
    """ EfficientNet-B5. Tensorflow compatible variant """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet(channel_multiplier=1.6, depth_multiplier=2.2, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_b5']))
    return model


def tf_efficientnet_b6(pretrained=False, **kwargs):
    """ EfficientNet-B6. Tensorflow compatible variant """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet(channel_multiplier=1.8, depth_multiplier=2.6, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_b6']))
    return model


def tf_efficientnet_b7(pretrained=False, **kwargs):
    """ EfficientNet-B7. Tensorflow compatible variant """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet(channel_multiplier=2.0, depth_multiplier=3.1, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_b7']))
    return model


def tf_efficientnet_es(pretrained=False, **kwargs):
    """ EfficientNet-Edge Small. Tensorflow compatible variant  """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet_edge(
        channel_multiplier=1.0, depth_multiplier=1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_es']))
    return model


def tf_efficientnet_em(pretrained=False, **kwargs):
    """ EfficientNet-Edge-Medium. Tensorflow compatible variant  """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet_edge(channel_multiplier=1.0, depth_multiplier=1.1, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_em']))
    return model


def tf_efficientnet_el(pretrained=False, **kwargs):
    """ EfficientNet-Edge-Large. Tensorflow compatible variant  """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet_edge(channel_multiplier=1.2, depth_multiplier=1.4, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_el']))
    return model


def tf_efficientnet_cc_b0_4e(pretrained=False, **kwargs):
    """ EfficientNet-B0 """
    # NOTE for train, drop_rate should be 0.2
    #kwargs['drop_connect_rate'] = 0.2  # set when training, TODO add as cmd arg
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet_condconv(channel_multiplier=1.0, depth_multiplier=1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_cc_b0_4e']))
    return model


def tf_efficientnet_cc_b0_8e(pretrained=False, **kwargs):
    """ EfficientNet-B0 """
    # NOTE for train, drop_rate should be 0.2
    #kwargs['drop_connect_rate'] = 0.2  # set when training, TODO add as cmd arg
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet_condconv(channel_multiplier=1.0, depth_multiplier=1.0, experts_multiplier=2, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_cc_b0_8e']))
    return model


def tf_efficientnet_cc_b1_8e(pretrained=False, **kwargs):
    """ EfficientNet-B0 """
    # NOTE for train, drop_rate should be 0.2
    #kwargs['drop_connect_rate'] = 0.2  # set when training, TODO add as cmd arg
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_efficientnet_condconv(channel_multiplier=1.0, depth_multiplier=1.1, experts_multiplier=2, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_efficientnet_cc_b1_8e']))
    return model


def mixnet_s(pretrained=False, **kwargs):
    """Creates a MixNet Small model.
    """
    model = _gen_mixnet_s(channel_multiplier=1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_mixnet_s']))
    return model


def mixnet_m(pretrained=False, **kwargs):
    """Creates a MixNet Medium model.
    """
    model = _gen_mixnet_m(channel_multiplier=1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['mixnet_m']))
    return model


def mixnet_l(pretrained=False, **kwargs):
    """Creates a MixNet Large model.
    """
    model = _gen_mixnet_m(channel_multiplier=1.3, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['mixnet_l']))
    return model


def mixnet_xl(pretrained=False, **kwargs):
    """Creates a MixNet Extra-Large model.
    Not a paper spec, experimental def by RW w/ depth scaling.
    """
    model = _gen_mixnet_m(channel_multiplier=1.6, depth_multiplier=1.2, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['mixnet_xl']))
    return model


def tf_mixnet_s(pretrained=False, **kwargs):
    """Creates a MixNet Small model. Tensorflow compatible variant
    """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_mixnet_s(channel_multiplier=1.0, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_mixnet_s']))
    return model


def tf_mixnet_m(pretrained=False, **kwargs):
    """Creates a MixNet Medium model. Tensorflow compatible variant
    """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_mixnet_m(channel_multiplier=1.0,  **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_mixnet_m']))
    return model


def tf_mixnet_l(pretrained=False, **kwargs):
    """Creates a MixNet Large model. Tensorflow compatible variant
    """
    kwargs['bn_eps'] = BN_EPS_TF_DEFAULT
    kwargs['pad_type'] = 'same'
    model = _gen_mixnet_m(channel_multiplier=1.3, **kwargs)
    if pretrained:
        model.load_state_dict(load_state_dict_from_url(model_urls['tf_mixnet_l']))
    return model
