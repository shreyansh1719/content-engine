# Three-Way Model Evaluation Report

Generated: 2026-03-12T22:50:06.898535

## Composite Score Summary

| Model | Mean ± Std | Min | Max | Successful |
|-------|-----------|-----|-----|-----------|
| Baseline (gpt-4.1-mini) | 71.5 ± 6.6 | 64.2 | 85.1 | 8/10 |
| SFT | 66.4 ± 10.7 | 48.0 | 86.1 | 10/10 |
| SFT+DPO | 71.4 ± 7.0 | 62.7 | 84.0 | 10/10 |

## Per-Metric Breakdown

| Metric | Baseline | SFT | SFT+DPO |
|--------|---------|-----|---------|
| Readability | 74.8 | 62.8 | 70.8 |
| Placement | 58.8 | 49.9 | 60.4 |
| Composition | 67.8 | 71.1 | 68.2 |
| Harmony | 98.8 | 100.0 | 99.7 |
| Copy | 72.8 | 72.8 | 76.7 |

## Pairwise Statistical Significance (Welch's t-test)

| Comparison | Δ Score | p-value | Significant |
|-----------|---------|---------|-------------|
| Baseline vs SFT | -5.1 | 0.2647 | n.s. |
| SFT vs SFT+DPO | +5.0 | 0.2586 | n.s. |
| Baseline vs SFT+DPO | -0.1 | 0.9891 | n.s. |

\* p<0.05, \** p<0.01, n.s. = not significant

## Winner

**Baseline (gpt-4.1-mini)** with mean composite score 71.5/100

## Model Migration Note

Migrated from deprecated `ft:gpt-4o-mini-2024-07-18` to `gpt-4.1-mini-2025-04-14`.
gpt-4.1-mini supports DPO fine-tuning (gpt-4o-mini does not).

- SFT model: `ft:gpt-4.1-mini-2025-04-14:shreyansh::DIb8s5h2`
- SFT+DPO model: `ft:gpt-4.1-mini-2025-04-14:shreyansh::DIdMhrba`