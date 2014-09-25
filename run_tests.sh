#!/bin/bash

#Checking in current platform
python -m unittest discover

#test in wine
wine python -m unittest discover
