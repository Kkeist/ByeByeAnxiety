"""
ByeByeAnxiety - ADHD Life Assistant
Main entry point for the application
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.ui import MainWindow


def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("ByeByeAnxiety")
    app.setOrganizationName("ByeByeAnxiety")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

