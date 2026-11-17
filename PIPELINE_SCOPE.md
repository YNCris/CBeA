# Pipeline stages and release coverage

The accompanying dataset separates two uses: a small real input/output demo for the compiled feature core, and complete retained derived observations for reproducing the manuscript statistics.

| Stage | In this candidate | Additional requirements for a complete raw-data rebuild |
|---|---|---|
| Microscopy acquisition | Two tracked-cell fixed crops, 16 frames each | Complete acquisition movies, timing and plate maps |
| CPDINO segmentation and Trackastra tracking | Frozen target-cell masks and centroid tracks for demo | External packages, original checkpoints, inference settings and full images |
| Fourier and centroid-motion features | Compiled original core plus public interface and expected demo outputs | Full tracked contours/coordinates for every cell |
| Dynamic temporal segmentation (ACA/DTAK) | Methods documented; no third-party implementation bundled | Separately obtained original ACA/DTAK and licensed MATLAB |
| Atlas fitting | Frozen 5,000-reference coordinates/assignments per separate model and displayed matrix overview | Full reference features, selections/seeds, fitted normalization, full pairwise similarities and UMAP dependencies |
| Point aggregation and inference | Complete derived point values; portable ANOVA/Tukey replay | Raw-to-point processing is upstream and not repeated by replay |
| Publication figures | Final reference PNGs and new quantitative diagnostic plots | Historical layout scripts and original representative image assets for exact layout reconstruction |

The original temporal segmentation used nMi=4 for initialization and maximum segment length 12; the unchanged original search can produce shorter segments. Training/refitting on the two supplied cells would not reconstruct the original atlas and is not claimed to do so.

The final analysis uses Ward clustering on its retained representation, not the historical Leiden/igraph trials. A display matrix downsample and frozen embedding coordinates are visualization results, not replacements for full atlas-fitting inputs. Cell models have separate class definitions.

The author-private archive retains project source snapshots, native source/build information and path-bearing provenance. It is separate from the binary repository. The historical source snapshot is an audit record with workstation paths, not an independently portable raw-image pipeline.

## Upstream software

- CPDINO/Cellpose: https://github.com/MouseLand/cellpose
- Trackastra: https://github.com/weigertlab/trackastra
- Original Behavior Atlas with nested ACA/DTAK components: https://github.com/huangkang314/Behavior-Atlas
- MATLAB: https://www.mathworks.com/products/matlab.html

Acquire these independently, under their respective terms. A top-level repository license must not be assumed to replace a restricted nested component's notice. Any separate institutional commercial authorization covers only rights the institution actually holds; it does not narrow permissions already granted by LICENSE. See THIRD_PARTY_NOTICES.md.

For the installed and verified native interface, see NATIVE_CORE_README.md. For reproduced model families, effect directions, statistical units, tolerances and commands, see REPLAY_README.md.

