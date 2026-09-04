---
title: HTDemucs Neural DSP
description: Hybrid Transformer architecture and acoustic signal separation principles.
---

## Theory of Audio Source Separation

Audio source separation is the mathematical task of decomposing an observed mixture waveform $x(t) \in \mathbb{R}^{C \times T}$ into $K$ individual acoustic sources:

$$x(t) = \sum_{k=1}^{K} s_k(t)$$

In commercial music production, these sources represent independent instrument stems such as vocals, drums, bass, and accompaniment.

## The Hybrid Transformer Architecture

Earlier neural separation models operated strictly in either the time domain (Wave-U-Net, Conv-TasNet) or the frequency domain (Open-Unmix, D3Net). Each approach presents fundamental trade-offs:
* **Time-domain models:** Excel at percussive attacks and transient timing, but suffer from high computational complexity on long audio sequences.
* **Frequency-domain models:** Computationally efficient on spectrogram representations, but discard phase information or create musical phase cancellation artifacts upon inversion.

Meta's **Hybrid Transformer Demucs (HTDemucs)** solves this by coupling both domains:
1. **Dual U-Net Encoders:** One encoder processes raw time-domain waveforms, while the other processes short-time Fourier transform (STFT) spectrograms.
2. **Cross-Domain Transformer:** The innermost latent features are fed to a Transformer Encoder. Self-attention models long-range temporal structure within each domain, while cross-attention exchanges representations across domains.
3. **Dual Decoders:** The network reconstructs both representations, synthesizing final audio stems with minimal artifacts and high Signal-to-Distortion Ratio (SDR).

## Official Meta Implementation

`audio-tools-for-agents` uses Alexandre Défossez's official upstream implementation (`demucs>=4.1.0`), ensuring access to canonical weights and PyTorch kernels without intermediate translation layers.
