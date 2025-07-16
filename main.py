#!/usr/bin/env python3
"""
Main entry point for OCR Intelligent
Launches Streamlit application with automatic port management
Compatible with Python 3.8+ including Python 3.13
"""
import os
import sys
import subprocess
import webbrowser
import time
import socket
import logging
from pathlib import Path

# Environment configuration for stability
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["PYTHONIOENCODING"] = "utf-8"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_port_in_use(port):
    """Check if a port is in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except Exception as e:
        logger.warning(f"Error checking port {port}: {e}")
        return False

def find_free_port(start_port=8501, max_attempts=20):
    """Find a free port for Streamlit with enhanced detection"""
    logger.info(f"Searching for free port starting from {start_port}...")

    for port in range(start_port, start_port + max_attempts):
        try:
            # Test port binding
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))

                # Double check that port is not in use
                if not check_port_in_use(port):
                    logger.info(f"Free port found: {port}")
                    return port

        except OSError:
            if port == start_port:
                logger.info(f"Port {port} occupied, searching for alternative...")
            continue

    # If no free port found, use random port
    import random
    fallback_port = random.randint(8600, 8700)
    logger.warning(f"No free port found, using fallback port: {fallback_port}")
    return fallback_port

def terminate_streamlit_processes():
    """Terminate existing Streamlit processes"""
    try:
        import psutil
        terminated_count = 0

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if it's a Streamlit process
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'streamlit' in cmdline.lower() and 'run' in cmdline.lower():
                        logger.info(f"Terminating Streamlit process (PID: {proc.info['pid']})")
                        proc.terminate()
                        terminated_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if terminated_count > 0:
            logger.info(f"{terminated_count} Streamlit processes terminated")
            time.sleep(2)
        else:
            logger.info("No running Streamlit processes found")

    except ImportError:
        logger.warning("psutil module not available, cannot check processes")
        logger.info("Process management will be limited")
    except Exception as e:
        logger.error(f"Error terminating processes: {e}")

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []

    try:
        import streamlit
        logger.info(f"Streamlit version: {streamlit.__version__}")
    except ImportError:
        missing_deps.append("streamlit")

    try:
        import psutil
        logger.info(f"psutil version: {psutil.__version__}")
    except ImportError:
        logger.warning("psutil not available - process management will be limited")

    if missing_deps:
        logger.error(f"Missing required dependencies: {', '.join(missing_deps)}")
        return False

    return True

def open_browser_delayed(url, delay=3):
    """Ouvre le navigateur après un délai"""
    import threading

    def delayed_open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"Navigateur ouvert: {url}")
        except Exception as e:
            print(f"Impossible d'ouvrir le navigateur: {e}")
            print(f"Ouvrez manuellement: {url}")

    thread = threading.Thread(target=delayed_open)
    thread.daemon = True
    thread.start()

def setup_environment():
    """Configure the execution environment"""
    # Add current directory to Python PATH
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    # Create necessary directories
    directories = ["output", "logs", "corrected"]
    for dir_name in directories:
        dir_path = current_dir / dir_name
        dir_path.mkdir(exist_ok=True)
        logger.info(f"Directory ready: {dir_path}")

    return current_dir

def main():
    """Main function with enhanced error handling for Python 3.13"""
    print("="*60)
    print("OCR INTELLIGENT - STARTING")
    print("="*60)
    print("Optical Character Recognition Application")
    print("Engines: Tesseract, EasyOCR, DocTR")
    print(f"Python version: {sys.version}")
    print("="*60)

    try:
        # Check dependencies first
        if not check_dependencies():
            logger.error("Required dependencies are missing")
            print("\n[ERROR] Required dependencies are missing!")
            print("Please run the Lancer_OCR_Intelligent.bat file to install dependencies")
            input("Press Enter to close...")
            return False

        # Environment setup
        current_dir = setup_environment()
        logger.info(f"Working directory: {current_dir}")

        # Check and terminate existing Streamlit processes
        logger.info("Checking for existing Streamlit processes...")
        terminate_streamlit_processes()

        # Find free port
        port = find_free_port()

        # Path to Streamlit application
        app_path = current_dir / "frontend" / "app.py"

        if not app_path.exists():
            logger.error(f"Application not found: {app_path}")
            print(f"ERROR: Application not found: {app_path}")
            print("Please verify that frontend/app.py exists")
            input("Press Enter to close...")
            return False
        
        # URL de l'application
        url = f"http://localhost:{port}"
        
        print(f"Port utilisé: {port}")
        print(f"URL: {url}")
        print("Démarrage en cours...")
        print("="*60)
        
        # Ouvrir le navigateur avec délai
        open_browser_delayed(url, delay=5)
        
        # Commande Streamlit avec gestion d'erreurs améliorée
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            str(app_path),
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        print("Lancement de Streamlit...")
        print("Appuyez sur Ctrl+C pour arrêter")
        print("="*60)
        
        # Lancer Streamlit avec retry en cas d'erreur de port
        max_retries = 3
        for attempt in range(max_retries):
            try:
                subprocess.run(cmd, check=True)
                return True
                
            except subprocess.CalledProcessError as e:
                if "Address already in use" in str(e) or "port" in str(e).lower():
                    print(f"Conflit de port détecté (tentative {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        # Trouver un nouveau port
                        port = find_free_port(port + 1)
                        url = f"http://localhost:{port}"
                        cmd[cmd.index("--server.port") + 1] = str(port)
                        print(f"Nouveau port: {port}")
                        continue
                    else:
                        print("Impossible de trouver un port libre après plusieurs tentatives")
                        return False
                else:
                    print(f"Erreur Streamlit: {e}")
                    return False
                    
            except KeyboardInterrupt:
                print("\nApplication fermée par l'utilisateur")
                return True
            except Exception as e:
                print(f"Erreur inattendue: {e}")
                if attempt < max_retries - 1:
                    print("Nouvelle tentative...")
                    time.sleep(2)
                    continue
                else:
                    return False
        
        return False
        
    except Exception as e:
        print(f"ERREUR: {e}")
        print("\nVérifiez que Python et Streamlit sont installés")
        input("Appuyez sur Entrée pour fermer...")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            input("Appuyez sur Entrée pour fermer...")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication fermée par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur fatale: {e}")
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)
