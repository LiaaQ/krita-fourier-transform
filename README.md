# Discrete Fourier Transform Krita Add-on

This is a simple Krita add-on that applies a Discrete Fourier Transform to images.  
I didn’t use Python’s built-in Fourier libraries — the transform is written from scratch.  
The goal was to understand how the Fourier Transform works in practice.

### Features
- Forward and inverse Fourier Transform.
- Written entirely in Python without external math/FFT functions.
- Basic integration with Krita as a plugin.

### Why
Mainly for learning purposes. I wanted to implement the math myself instead of relying on existing functions.

### Status
Very basic — expect slow performance on larger images.  
Good enough for experimenting and understanding the transform process.

![Result](./2d.png)
