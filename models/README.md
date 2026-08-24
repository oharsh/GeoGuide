# Trained models

`object_classification.h5` lives here at run time but is not tracked in git —
it is a fine-tuned InceptionV3 checkpoint, too large to version sensibly.

Two ways to get it:

- **Train it yourself.** Unpack the dataset zips from `data/datasets/` into
  `runtime/dataset/train/<class>/` and `runtime/dataset/test/<class>/`, then run
  `python training/train_classifier.py`. It writes the weights straight here.
- **Download the checkpoint** trained during the original build:
  <https://drive.google.com/file/d/1BZF8WWO4OBdTA7PnIGOTsOfYp40APhCW/view?usp=drive_link>

Point `control_center/config.py` elsewhere with `GEOGUIDE_MODEL=/path/to/weights.h5`
if you keep it somewhere else.
