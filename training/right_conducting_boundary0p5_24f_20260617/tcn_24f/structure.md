# TCN Conducting Probe Structure

```text
input: [B, 9, T]
channels: right shoulder/elbow/wrist x/y/confidence flattened
encoder: causal Conv1d residual TCN
hidden_channels: 64
levels: 4
kernel_size: 5
heads: tempo 4-class, gain 2-class
loss: CE tempo + 0.5 CE gain
```
