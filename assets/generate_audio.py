"""Genera efectos de sonido simples para el juego Flappy Bird.
Usa solo módulos built-in de Python (wave, struct, math) - sin costo."""
import struct
import math
import os

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

SAMPLE_RATE = 22050

def generate_wav(filename, duration_sec, frequency_func, volume=0.5):
    """Genera un archivo WAV con la función de frecuencia dada."""
    n_samples = int(SAMPLE_RATE * duration_sec)
    
    with open(filename, 'wb') as wav:
        # WAV header
        wav.write(b'RIFF')
        wav.write(struct.pack('<I', 36 + n_samples * 2))  # file size - 8
        wav.write(b'WAVE')
        wav.write(b'fmt ')
        wav.write(struct.pack('<I', 16))  # chunk size
        wav.write(struct.pack('<H', 1))   # PCM format
        wav.write(struct.pack('<H', 1))   # mono
        wav.write(struct.pack('<I', SAMPLE_RATE))
        wav.write(struct.pack('<I', SAMPLE_RATE * 2))  # byte rate
        wav.write(struct.pack('<H', 2))   # block align
        wav.write(struct.pack('<H', 16))  # bits per sample
        wav.write(b'data')
        wav.write(struct.pack('<I', n_samples * 2))
        
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            freq = frequency_func(t)
            sample = int(volume * 32767 * math.sin(2 * math.pi * freq * t))
            # Aplicar envolvente para evitar clicks
            env = min(1.0, min(t * 50, (duration_sec - t) * 50))
            sample = int(sample * env)
            wav.write(struct.pack('<h', max(-32768, min(32767, sample))))

def jump_sound(t):
    """Sueno de salto: tono ascendente rápido"""
    return 300 + t * 800

def score_sound(t):
    """Sueno de punto: campanilla aguda"""
    freq = 880
    return freq + math.sin(t * 20) * 100

def death_sound(t):
    """Sueno de muerte: tono descendente"""
    return max(100, 400 - t * 200)

def music_loop(t):
    """Música de fondo simple (8-bit style) - loop de 2 segundos."""
    # Loop de la música
    t = t % 2.0
    # Base rhythm - 120 BPM
    note_t = t % 0.5
    if t < 1.0:
        freq = 220
    else:
        freq = 330
    # Simple arpegio
    arp_t = t % 0.25
    return freq + arp_t * 100

print("Generando efectos de sonido...")

generate_wav(os.path.join(AUDIO_DIR, "jump.wav"), 0.15, jump_sound, 0.4)
print("  jump.wav creado")

generate_wav(os.path.join(AUDIO_DIR, "score.wav"), 0.2, score_sound, 0.3)
print("  score.wav creado")

generate_wav(os.path.join(AUDIO_DIR, "death.wav"), 0.4, death_sound, 0.5)
print("  death.wav creado")

# Para la música de fondo, generamos 30 segundos de loop
print("Generando música de fondo (30 seg)...")
def background_music(t):
    """Música chill/lofi simple para el fondo."""
    # BPM 100, compás de 4
    beat = t * (100 / 60)
    bar = beat % 4
    
    # Base constante suave
    if bar < 1:
        freq = 165  # E3
    elif bar < 2:
        freq = 196  # G3
    elif bar < 3:
        freq = 220  # A3
    else:
        freq = 196  # G3
    
    # Añadir arpegio de vez en cuando
    if bar < 0.25:
        freq = 330  # E4
    elif bar < 0.5:
        freq = 392  # G4
    elif bar < 0.75:
        freq = 440  # A4
    
    return freq

generate_wav(os.path.join(AUDIO_DIR, "music.mp3"), 30, background_music, 0.2)
print("  music.mp3 creado")

print("\nListo! Archivos de audio en:")
for f in os.listdir(AUDIO_DIR):
    path = os.path.join(AUDIO_DIR, f)
    size = os.path.getsize(path)
    print(f"  {f}: {size:,} bytes")