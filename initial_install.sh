#!/bin/bash

sudo apt install ffmpeg
conda create --name=discordTest python=3.6
source activate discordTest
pip install -U "discord.py[voice]"
pip install python-dotenv
pip install numpy
conda install h5py
pip install asyncpg
pip install gTTS
