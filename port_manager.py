#!/usr/bin/env python3
"""
Utilitaire de gestion des ports pour OCR Intelligent
Permet de diagnostiquer et résoudre les conflits de ports
"""
import socket
import subprocess
import sys
from pathlib import Path

def check_port_status(port):
    """Vérifie le statut d'un port"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def find_streamlit_processes():
    """Trouve les processus Streamlit en cours"""
    try:
        import psutil
        streamlit_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'streamlit' in cmdline.lower() and 'run' in cmdline.lower():
                        streamlit_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return streamlit_processes
    except ImportError:
        print("Module psutil non disponible")
        return []

def kill_streamlit_processes():
    """Termine tous les processus Streamlit"""
    try:
        import psutil
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'streamlit' in cmdline.lower() and 'run' in cmdline.lower():
                        proc.terminate()
                        killed_count += 1
                        print(f"Processus terminé: PID {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return killed_count
    except ImportError:
        print("Module psutil non disponible")
        return 0

def find_available_ports(start_port=8501, count=10):
    """Trouve les ports disponibles"""
    available_ports = []
    
    for port in range(start_port, start_port + count):
        if not check_port_status(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    available_ports.append(port)
            except:
                continue
    
    return available_ports

def main():
    """Fonction principale"""
    print("="*60)
    print("GESTIONNAIRE DE PORTS - OCR INTELLIGENT")
    print("="*60)
    
    # Vérifier les ports couramment utilisés
    print("\n[STEP] Vérification des ports...")
    common_ports = [8501, 8502, 8503, 8504, 8505]
    
    for port in common_ports:
        status = "OCCUPÉ" if check_port_status(port) else "LIBRE"
        print(f"Port {port}: {status}")
    
    # Chercher les processus Streamlit
    print("\n[STEP] Recherche des processus Streamlit...")
    streamlit_procs = find_streamlit_processes()
    
    if streamlit_procs:
        print(f"Trouvé {len(streamlit_procs)} processus Streamlit:")
        for proc in streamlit_procs:
            print(f"  PID {proc['pid']}: {proc['cmdline'][:80]}...")
        
        # Proposer de les terminer
        response = input("\nTerminer tous les processus Streamlit? (o/N): ").strip().lower()
        if response in ['o', 'oui', 'y', 'yes']:
            killed = kill_streamlit_processes()
            print(f"{killed} processus terminés")
    else:
        print("Aucun processus Streamlit trouvé")
    
    # Trouver des ports disponibles
    print("\n[STEP] Recherche de ports disponibles...")
    available = find_available_ports()
    
    if available:
        print(f"Ports disponibles: {', '.join(map(str, available[:5]))}")
        print(f"Port recommandé: {available[0]}")
    else:
        print("Aucun port disponible dans la plage 8501-8510")
    
    print("\n" + "="*60)
    print("DIAGNOSTIC TERMINÉ")
    print("="*60)
    
    if streamlit_procs and not available:
        print("RECOMMANDATION: Redémarrez votre ordinateur pour libérer les ports")
    elif available:
        print(f"RECOMMANDATION: Utilisez le port {available[0]} pour Streamlit")
    
    print("\nPour lancer OCR Intelligent, utilisez:")
    print("  python main.py")
    print("  ou")
    print("  Lancer_OCR_Intelligent.bat")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOpération annulée")
    except Exception as e:
        print(f"Erreur: {e}")
    
    input("\nAppuyez sur Entrée pour fermer...")
