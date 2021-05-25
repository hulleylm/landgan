# Landscape_GAN

![Generated sat images](./readmeImages/512generated.png)

**Picture:** *These are not real satellite images. They were generated using the methods discussed in this project.*

This repository contains my final year undergraduate dissertation and the code used to generate the results.

> **Generative Adversarial Networks for Terrain Generation**<br>
> The full dissertation can be viewed [here](https://drive.google.com/file/d/16sgsRHorQmk6zuQylsT1Qiitose17SVA/view?usp=sharing)
>
> **Abstract:** *For decades, procedural terrain generation methods have been based on fractal and noise based techniques. This work proposes that GANs, specifically the StyleGAN architecture, are a suitable alternative method of terrain generation. Multiple datasets are created and used to train a StyleGAN2 model. The results are then displayed as 3D terrains and compared against traditional techniques.*

![Generated unity models](./readmeImages/512Unity.png)

Final year project for BSc Computer Science at the University of Liverpool.

Training on 2,500 128x128 RGBA satellite images over 1,200 epochs (animated gif).
Combined RGBA images (set to a white background)

![](readmeImages/comboSmall.gif)

RGB images (above images seperated to just the first three channels)

![](readmeImages/imagesSmall.gif)

Heightmap channel (final channel of original image)

![](readmeImages/heightSmall.gif)
