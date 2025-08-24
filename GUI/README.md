Install
sudo apt update
sudo apt install -y python3 python3-pyqt5 python3-pyqt5.qtwebengine xdotool
sudo dpkg -i guacagui_1.0-2_all.deb
# If dpkg complains about deps:
sudo apt -f install