# Notebooks

Run on Kaggle in this order: `02_preprocessing.ipynb` →
`04_model_seeds.ipynb`. Attach the [TLVMC Parkinson's Freezing of Gait
dataset](https://www.kaggle.com/competitions/tlvmc-parkinsons-freezing-gait-prediction)
to both sessions; do not redistribute the data.

`02_preprocessing.ipynb` writes `windows_meta.parquet`, `window_feats.npy`, and
`windows_X.npy`, and bundles its deliverables as `asha_outputs.zip` in
`/kaggle/working`. `04_model_seeds.ipynb` then writes the seed-averaged
`oof_C_mean.npy`.

`scripts/export_signal_snippets.py` reads only the two files named in its
`REQUIRED` tuple — `windows_meta.parquet` and `windows_X.npy` — so those two
must exist in the artifact directory before it runs; `window_feats.npy` and
`oof_C_mean.npy` are outputs of the notebooks, not inputs to that script.

`scripts/merge_signal_fragment.py` is an alternative, hash-validated merge path
for a signal-fragment JSON. No file in this repository produces such a
fragment; the in-repo path is `export_signal_snippets.py`, which writes
`signal_snippets` straight into `dashboard/twin_data.json`.

`02_preprocessing.ipynb` takes approximately 1.5 h on Kaggle GPU.

`*.npy` and `*.parquet` are gitignored by design and must be regenerated.
