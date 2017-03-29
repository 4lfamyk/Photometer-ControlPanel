#!/bin/bash

sudo modprobe fbtft_device custom name=fb_ili9341 gpios=reset:22,dc:5,led:6 speed=16000000 rotate=180 txbuflen=32768 bgr=1
sudo FRAMEBUFFER=/dev/fb1 startx
