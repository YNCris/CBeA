# Analysis pipeline and available workflows

The study combines cell-shape dynamics and locomotion to identify stereotyped behavioral motifs. The processing sequence is:

```text
Live-cell images
  → cell segmentation and tracking
  → Fourier shape descriptors and centroid motion
  → dynamic temporal segmentation and DTAK similarity
  → behavior atlas embedding and motif identification
  → point-level motif fractions and treatment comparisons
```

The repository provides an executable feature demonstration and statistical reproduction workflow. The Zenodo deposit supplies their inputs and the retained analysis outputs.

| Stage | Available material | Requirements for a complete raw-image analysis |
| --- | --- | --- |
| Imaging | Two tracked-cell image sequences, each with 16 frames | Complete acquisition movies, timing, and plate maps |
| CPDINO segmentation and Trackastra tracking | Target-cell masks and centroid tracks for the demonstration | Full images, model weights, and inference settings |
| Fourier descriptors and motion | Compiled feature module, Python interface, and reference features | Tracked contours and centroids for every cell |
| Dynamic temporal segmentation and DTAK similarity | Segmented behavior and atlas outputs in the derived data | Full feature sequences and the upstream temporal-analysis software |
| Atlas construction | 5,000 reference coordinates and assignments per cell model, plus the displayed similarity overview | Reference feature sequences, full similarities, normalization, and embedding parameters |
| Statistical analysis | Point-level measurements and executable ANOVA/Tukey calculations | Included in the deposited derived-data workflow |
| Figures | Reference figure PNGs and independently regenerated quantitative plots | Representative images and layout assets for exact figure composition |

The temporal analysis used a four-frame initialization minimum and a twelve-frame maximum segment length. Shorter segments produced by the temporal search were retained. Motif identification used Ward hierarchical clustering. MDA-MB-231 and iDMSC have separate motif definitions.

The minimal examples demonstrate feature computation for individual cells. Complete atlas refitting requires the full inputs listed above; the deposited reference coordinates and displayed similarity overview are visualization outputs rather than substitutes for those inputs.

## Upstream software

- [CPDINO/Cellpose](https://github.com/MouseLand/cellpose): cell segmentation.
- [Trackastra](https://github.com/weigertlab/trackastra): cell tracking.
- [Behavior Atlas](https://github.com/huangkang314/Behavior-Atlas): temporal analysis and DTAK similarity.
- [MATLAB](https://www.mathworks.com/products/matlab.html): runtime for the upstream temporal-analysis implementation.

Upstream software is obtained separately under its own terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Running the available workflows

Use [NATIVE_CORE_README.md](NATIVE_CORE_README.md) for the real-cell feature demonstration and [REPLAY_README.md](REPLAY_README.md) for the figure-level statistical calculations. The [dataset record](https://doi.org/10.5281/zenodo.24302450) and its data dictionary document the input variables, units, and cell-model-specific motif definitions.
