#!/usr/bin/env python
# coding=utf-8
# wujian@2018

import argparse
import os

import numpy as np
from scipy.io import loadmat

from utils import istft, get_logger
from data_handler import SpectrogramReader
from beamformer import FixedBeamformer

logger = get_logger(__name__)


def run(args):
    stft_kwargs = {
        "frame_length": args.frame_length,
        "frame_shift": args.frame_shift,
        "window": args.window,
        "center": args.center,
        "transpose": False
    }
    spectrogram_reader = SpectrogramReader(args.wav_scp, **stft_kwargs)
    weights_dict = loadmat(args.weights)
    if args.weight_key not in weights_dict:
        raise KeyError("Weight key error: no \'{}\' in {}".format(
            args.weight_key, args.weights))

    beamformer = FixedBeamformer(weights_dict[args.weight_key])
    num_utts = 0
    for key, stft_mat in spectrogram_reader:
        num_utts += 1
        logger.info("Processing utterance {}".format(key))
        stft_enh = beamformer.run(stft_mat)
        # do not normalize
        istft(
            os.path.join(args.dst_dir, '{}.wav'.format(key)), stft_enh,
            **stft_kwargs)
    logger.info("Processed {} utterances".format(num_utts))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Command to run fixed beamformer")
    parser.add_argument(
        'wav_scp', type=str, help="Multi-channel wave scripts in kaldi format")
    parser.add_argument(
        'weights', type=str, help="Fixed beamformer weight in MATLAB format")
    parser.add_argument(
        'dst_dir', type=str, help="Location to dump enhanced wave file")
    parser.add_argument(
        "--frame-length",
        type=float,
        default=1024,
        dest="frame_length",
        help="Frame length in number of samples")
    parser.add_argument(
        "--frame-shift",
        type=float,
        default=256,
        dest="frame_shift",
        help="Frame shift in number of samples")
    parser.add_argument(
        "--center",
        action="store_true",
        default=False,
        dest="center",
        help="\'center\' flags in librosa.stft functions")
    parser.add_argument(
        "--window",
        default="hann",
        dest="window",
        help="Type of window function, see scipy.signal.get_window")
    parser.add_argument(
        "--weight-key",
        default="weights",
        dest="weight_key",
        help="String key to index matrix in MATLAB's .mat file")
    args = parser.parse_args()
    run(args)

    