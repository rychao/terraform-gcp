#!/bin/bash
# Script to install Python Selenium and Headless Chrome

#Python Imports
sleep 15
sudo apt -y update
sudo apt -y install python3-pip
pip3 install selenium

#Install Chromedriver
curl -O https://chromedriver.storage.googleapis.com/87.0.4280.88/chromedriver_linux64.zip
sudo apt -y install unzip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/.

#Install Chrome Browser
sudo add-apt-repository -y ppa:canonical-chromium-builds/stage
sudo apt-get -y install chromium-browser
