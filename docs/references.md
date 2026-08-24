# References

Material collected while building this. Kept because a good chunk of it is not
easy to rediscover.

## QGIS and live tracking

- [QGIS basic map training manual](https://docs.qgis.org/3.28/en/docs/training_manual/basic_map/overview.html)
- [Real-time live data visualisation in QGIS](https://www.geodose.com/2020/09/realtime%20live%20data%20visualization%20qgis.html)
  — the approach `live.csv` is built around
- [Georeferencing a raster in QGIS](https://www.youtube.com/watch?v=l5UQekQzemE)
- [Working with delimited text layers](https://www.youtube.com/watch?v=kL-IEn22z8E)
- [Adding a live-updating point layer](https://www.youtube.com/watch?v=jKLBFddpTGI&t=178s)

## Image classification and transfer learning

- [Object detection vs image classification vs keypoint detection](https://blog.roboflow.com/object-detection-vs-image-classification-vs-keypoint-detection/)
  — why this project classifies pre-cropped regions rather than running a
  detector over the whole arena
- [Transfer learning guide](https://www.v7labs.com/blog/transfer-learning-guide)
- Learn PyTorch: [computer vision](https://www.learnpytorch.io/03_pytorch_computer_vision/),
  [custom datasets](https://www.learnpytorch.io/04_pytorch_custom_datasets/),
  [transfer learning](https://www.learnpytorch.io/06_pytorch_transfer_learning/)
- [Fine-tuning InceptionV3 in Keras](https://www.youtube.com/watch?v=NmLK_WQBxB4)
- [Training an image classifier end to end](https://www.youtube.com/watch?v=pDdP0TFzsoQ)

## OpenCV and ArUco

- [ArUco marker detection walkthrough](https://www.youtube.com/watch?v=s8dyBoQBCw8)
  — the camera calibration and pose estimation flow the `vision/` scripts follow
- [Drawing rectangles with text labels](https://stackoverflow.com/questions/56108183/python-opencv-cv2-drawing-rectangle-with-text)
- [Contour detection basics](https://www.youtube.com/watch?v=QG1Kc8ozfcM)

## Hardware

See [hardware.md](hardware.md) for sensor and motor driver links.
