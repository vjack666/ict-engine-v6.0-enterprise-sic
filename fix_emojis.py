#!/usr/bin/env python3
"""
Script para eliminar emojis de main.py y solucionar problemas de codificación
"""

import re

def remove_emojis_from_file(file_path):
    """Eliminar emojis de un archivo Python"""
    
    # Leer el archivo con codificación UTF-8
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazos específicos
    replacements = {
        '📊': '[DATA]',
        '✅': '[OK]',
        '⚠️': '[WARN]',
        '🔗': '[LINK]',
        '🧠': '[BRAIN]',
        '📱': '[MOBILE]',
        '🚀': '[ROCKET]',
        '💡': '[BULB]',
        '🎯': '[TARGET]',
        '📈': '[CHART]',
        '🔧': '[TOOL]',
        '⭐': '[STAR]',
        '🌟': '[GLOW]',
        '💎': '[DIAMOND]',
        '🔥': '[FIRE]',
        '💪': '[STRONG]',
        '🎉': '[PARTY]',
        '🏆': '[TROPHY]',
        '🚨': '[ALERT]',
        '❗': '[!]',
        '❓': '[?]',
        '❌': '[X]',
        '✔️': '[CHECK]',
        '➡️': '[->]',
        '⬅️': '[<-]',
        '⬆️': '[UP]',
        '⬇️': '[DOWN]'
    }
    
    # Aplicar reemplazos
    for emoji, replacement in replacements.items():
        content = content.replace(emoji, replacement)
    
    # Patrón para capturar otros emojis Unicode
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    content = emoji_pattern.sub('[EMOJI]', content)
    
    # Escribir el archivo limpio
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Emojis eliminados de {file_path}")

if __name__ == "__main__":
    remove_emojis_from_file("main.py")
    print("¡Proceso completado!")
