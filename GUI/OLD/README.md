## Install instructions

Install the required dependencies via apt (if they aren’t already present):

```bash
sudo apt update
sudo apt install python3 python3-pyqt5 python3-pyqt5.qtwebengine
```

Download the Debian package I built (see the file below) and install it:

```bash
sudo dpkg -i browser-app_1.0_all.deb
```

After installation you can launch the application from your application menu as Browser App or run browser-app from a terminal. The configuration file is installed under /usr/share/browser-app/config.json; editing the home_url value will change the startup page.

If you want to run it in Windows, you need to compile it for it,