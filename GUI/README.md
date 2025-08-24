# GuacaGUI

A custom web browser specifically designed for Apache Guacamole with enhanced console-friendly features. This application provides a minimal GUI with powerful tools for system administrators and developers working with remote consoles.

## 🚀 Features

- **Minimal GUI**: Clean, distraction-free interface optimized for console work
- **Draggable Tabs**: Flexible tab management for multiple console sessions
- **Textbox Macros**: Store and quickly paste commonly used commands and strings
- **Console Integration**: Seamless integration with Apache Guacamole
- **Cross-Platform**: Available for Linux and Windows
- **Customizable**: Configurable startup page and settings

## 🎯 Use Cases

- **System Administration**: Manage multiple servers through Guacamole
- **Development Work**: Quick access to development environments
- **Troubleshooting**: Efficient console access during incident response
- **Training**: Provide students with pre-configured console access

## 📋 Prerequisites

### Linux
- Ubuntu 18.04+ / Debian 9+ / CentOS 7+
- Python 3.6+
- Qt5 WebEngine support

### Windows
- Windows 10+ (64-bit)
- Compiled version available

## 🛠️ Installation

### Option 1: Debian Package (Recommended)

```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install -y python3 python3-pyqt5 python3-pyqt5.qtwebengine xdotool

# Install the application
sudo dpkg -i guacagui_1.0-2_all.deb

# Fix any dependency issues (if needed)
sudo apt -f install
```

### Option 2: Python Script

```bash
# Install Python dependencies
sudo apt update
sudo apt install -y python3 python3-pyqt5 python3-pyqt5.qtwebengine xdotool

# Clone the repository and run directly
git clone <repository-url>
cd Guacamole/GUI
python3 guacagui.py
```

### Option 3: Windows

Download the compiled Windows executable from the releases section.

## 🚀 Quick Start

### 1. Launch the Application

```bash
# From terminal
guacagui

# Or from application menu
# Applications → Internet → GuacaGUI
```

### 2. Configure Your Guacamole URL

The application uses a configuration file to define Guacamole URL and the Macros:

1. Navigate to the configuration file foler (in Ubuntu: nano /usr/share/guacagui/config.json)
2. You can update the config file with your specific settings
3. Restart GuacaGUI

### 3. Use Console Features

- **Tabs**: Drag and drop tabs to reorganize your console sessions
- **Macros**: Click on macro textboxes to copy commonly used commands
- **Console Mode**: Optimized interface for terminal work

## ⚙️ Configuration

### Configuration File Location

```bash
# Linux
/usr/share/guacagui/config.json

# User-specific (if available)
~/.config/guacagui/config.json
```

### Key Configuration Options

```json
}
  "home_url": "http://localhost:8080/guacamole/",
  "macros": [
    {"name": "1", "text": "sebastian.garcia"},
    {"name": "4", "text": "sudo apt update"},
    {"name": "5", "text": "docker compose up -d"},
    {"name": "6", "text": "docker compose down"}
  ]
}
```

### Customizing Macros

Edit the configuration file to add your commonly used commands:

```json
  "macros": [
    {"name": "1", "text": "sebastian.garcia"},
    {"name": "4", "text": "sudo apt update"},
    {"name": "5", "text": "docker compose up -d"},
    {"name": "6", "text": "docker compose down"}
  ]
```

## 🎮 Usage Guide

### Tab Management

- **Drag & Drop**: Click and drag tabs to reorder them

### Macro System

1. **Store Commands**: Add frequently used commands to macro textboxes
2. **Quick Access**: Click on any macro to copy its content
3. **Paste in Console**: Use `Ctrl+V` or right-click  or MMB → Paste in your console
4. **Customize**: Edit macros through the configuration file (Direct updates in the text boxses are not saved)

### Console Optimization

- See connection setting in Settings section

## 🔧 Troubleshooting

### Common Issues

#### 1. Application Won't Start

```bash
# Check Python installation
python3 --version

# Verify Qt dependencies
python3 -c "from PyQt5.QtWebEngineWidgets import QWebEngineView; print('Qt WebEngine OK')"

# Check for missing packages
ldd $(which python3) | grep -i qt
```

#### 2. Dependencies Missing

```bash
# Install all required packages
sudo apt install -y python3 python3-pyqt5 python3-pyqt5.qtwebengine xdotool

# For older Ubuntu/Debian versions
sudo apt install -y python3-pyqt5.qtwebengine
```

#### 3. Permission Issues

```bash
# Fix package installation issues
sudo dpkg --configure -a
sudo apt -f install

# Check file permissions
ls -la /usr/share/guacagui/
```

### Debug Mode

Run with verbose output for troubleshooting:

```bash
python3 guacagui.py --debug
```

## 🏗️ Development

### Building from Source

```bash
# Clone repository
git clone <repository-url>
cd Guacamole/GUI

# Install development dependencies
sudo apt install -y python3-dev python3-pip build-essential

# Install Python packages
pip3 install -r requirements.txt

# Run in development mode
python3 guacagui.py
```

### Building Debian Package

```bash
# Install build tools
sudo apt install -y devscripts debhelper

# Build package
debuild -b -uc -us
```

## 📁 Project Structure

```
GUI/
├── guacagui.py              # Main application script
├── guacagui_1.0-2_all.deb  # Debian package
├── config.json              # Configuration template
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 Python style guidelines
- Add comments for complex logic
- Test on both Linux and Windows
- Update documentation for new features

## 📚 Additional Resources

- [Apache Guacamole Documentation](https://guacamole.apache.org/doc/gug/)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [Qt WebEngine Documentation](https://doc.qt.io/qt-5/qtwebengine-index.html)

## 📄 License

This project is licensed under the same license as Apache Guacamole.

## ⚠️ Disclaimer

This application is provided as-is for educational and development purposes. For production use, ensure proper security hardening and testing are in place.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information:
   - Operating system and version
   - Python version
   - Error messages
   - Steps to reproduce

---

**Made with ❤️ for the Apache Guacamole community**
