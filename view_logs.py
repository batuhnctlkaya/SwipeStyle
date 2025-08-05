#!/usr/bin/env python3
"""
SwipeStyle Log Viewer
====================

Bu script agent_output_log.txt dosyasını daha okunabilir şekilde görüntüler.

Kullanım:
    python view_logs.py                    # Tüm logları göster
    python view_logs.py --last 10         # Son 10 girişi göster
    python view_logs.py --type question    # Sadece soru türü logları göster
    python view_logs.py --tail             # Canlı takip modu
"""

import sys
import argparse
import time
import os
from datetime import datetime

def print_colored(text, color='white'):
    """Renkli çıktı için ANSI kodları"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def parse_log_entry(lines, start_idx):
    """Bir log girişini parse eder"""
    entry = {
        'timestamp': '',
        'type': '',
        'input': '',
        'output': '',
        'raw_lines': []
    }
    
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        entry['raw_lines'].append(lines[i])
        
        if line.startswith('⏰ [') and 'Agent Output Type:' in line:
            # Timestamp ve type çıkar
            parts = line.split('] Agent Output Type: ')
            if len(parts) == 2:
                entry['timestamp'] = parts[0].replace('⏰ [', '')
                entry['type'] = parts[1]
        
        elif line.startswith('🔍 [') and 'CATEGORY DETECTION' in line:
            # Category detection
            parts = line.split('] ')
            if len(parts) >= 2:
                entry['timestamp'] = parts[0].replace('🔍 [', '')
                entry['type'] = 'category_detection'
        
        elif line.startswith('🌐 [') and 'API RESPONSE:' in line:
            # API response
            parts = line.split('] API RESPONSE: ')
            if len(parts) == 2:
                entry['timestamp'] = parts[0].replace('🌐 [', '')
                entry['type'] = f"api_response_{parts[1]}"
        
        elif line.startswith('📥 INPUT DATA:'):
            # Input data başlıyor
            i += 1
            input_lines = []
            while i < len(lines) and not lines[i].strip().startswith('-'):
                input_lines.append(lines[i])
                i += 1
            entry['input'] = ''.join(input_lines).strip()
            continue
        
        elif line.startswith('📤 OUTPUT DATA:') or line.startswith('INPUT:') or line.startswith('OUTPUT:'):
            # Output data başlıyor
            i += 1
            output_lines = []
            while i < len(lines) and not lines[i].strip().startswith('=') and not lines[i].strip().startswith('🔍') and not lines[i].strip().startswith('🌐') and not lines[i].strip().startswith('⏰'):
                if lines[i].strip() and not lines[i].strip().startswith('-'):
                    output_lines.append(lines[i])
                i += 1
            entry['output'] = ''.join(output_lines).strip()
            break
        
        # Eğer yeni bir entry başlıyorsa dur
        elif (line.startswith('⏰ [') or line.startswith('🔍 [') or line.startswith('🌐 [')) and i != start_idx:
            break
            
        i += 1
    
    return entry, i

def view_logs(filename='agent_output_log.txt', last_n=None, filter_type=None, tail=False):
    """Log dosyasını görüntüler"""
    
    if not os.path.exists(filename):
        print_colored(f"❌ Log dosyası bulunamadı: {filename}", 'red')
        return
    
    if tail:
        print_colored("📡 Canlı takip modu başlatılıyor... (Ctrl+C ile çıkış)", 'yellow')
        print_colored("-" * 80, 'cyan')
        
        # Dosyanın son konumunu takip et
        with open(filename, 'r', encoding='utf-8') as f:
            f.seek(0, 2)  # Dosyanın sonuna git
            
            try:
                while True:
                    line = f.readline()
                    if line:
                        print(line, end='')
                    else:
                        time.sleep(0.1)
            except KeyboardInterrupt:
                print_colored("\n\n👋 Canlı takip sonlandırıldı", 'yellow')
                return
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print_colored(f"❌ Dosya okuma hatası: {e}", 'red')
        return
    
    if not lines:
        print_colored("📝 Log dosyası boş", 'yellow')
        return
    
    # Log girişlerini parse et
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('⏰ [') or line.startswith('🔍 [') or line.startswith('🌐 ['):
            entry, next_i = parse_log_entry(lines, i)
            if entry['timestamp']:  # Geçerli entry
                entries.append(entry)
            i = next_i
        else:
            i += 1
    
    # Filtreleme
    if filter_type:
        entries = [e for e in entries if filter_type.lower() in e['type'].lower()]
    
    # Son N girişi
    if last_n:
        entries = entries[-last_n:]
    
    if not entries:
        print_colored("📝 Gösterilecek log girişi bulunamadı", 'yellow')
        return
    
    print_colored(f"📊 Toplam {len(entries)} log girişi bulundu", 'green')
    print_colored("=" * 80, 'cyan')
    
    # Girişleri göster
    for i, entry in enumerate(entries, 1):
        print_colored(f"\n📋 {i}. GİRİŞ", 'bold')
        print_colored(f"⏰ Zaman: {entry['timestamp']}", 'blue')
        print_colored(f"🏷️  Tür: {entry['type']}", 'purple')
        
        if entry['input']:
            print_colored("📥 INPUT:", 'yellow')
            print(entry['input'][:500] + "..." if len(entry['input']) > 500 else entry['input'])
        
        if entry['output']:
            print_colored("📤 OUTPUT:", 'green')
            print(entry['output'][:500] + "..." if len(entry['output']) > 500 else entry['output'])
        
        print_colored("-" * 80, 'cyan')

def main():
    parser = argparse.ArgumentParser(description='SwipeStyle Agent Log Viewer')
    parser.add_argument('--last', type=int, help='Son N girişi göster')
    parser.add_argument('--type', help='Belirli tür logları filtrele (question, recommendation, error, etc.)')
    parser.add_argument('--tail', action='store_true', help='Canlı takip modu')
    parser.add_argument('--file', default='agent_output_log.txt', help='Log dosyası yolu')
    
    args = parser.parse_args()
    
    try:
        view_logs(
            filename=args.file,
            last_n=args.last,
            filter_type=args.type,
            tail=args.tail
        )
    except KeyboardInterrupt:
        print_colored("\n\n👋 İşlem iptal edildi", 'yellow')

if __name__ == '__main__':
    main()
