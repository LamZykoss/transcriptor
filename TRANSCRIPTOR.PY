import os
import tempfile
import wave
import pyaudio
import keyboard
import pyautogui
import pyperclip
from groq import Groq

client = Groq(api_key="pon tu api-key de qroq") ## LINK: https://groq.com/

def grabar_audio(frecuencia=16000, canales=1, fragmento=1024):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=canales,
        rate=frecuencia,
        input=True,
        frames_per_buffer=fragmento,)
    print("Manten presionada la tecla de espacio")
    frames = []
    keyboard.wait('space')
    print("Grabando... (Suelta espacio para detener)")
    while keyboard.is_pressed('space'):
        data = stream.read(fragmento)
        frames.append(data)
    print("Grabación finalizada.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    return frames, frecuencia

def guardar(frames, frecuencia):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_temp:
        wf = wave.open(audio_temp.name, mode="wb")
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(frecuencia)
        wf.writeframes(b"".join(frames))
        wf.close()
        return audio_temp.name

def transcript(ruta_archivo):
    try:
        with open(ruta_archivo, "rb") as archivo:
            transcripcion = client.audio.transcriptions.create(
                file=(os.path.basename(ruta_archivo), archivo.read()),
                model="whisper-large-v3",
                prompt= "", ##poner contextom tal que la IA, pueda crear alguna idea y no equivocarse al transcribir.
                response_format="text",
                language='es'
            )
        return transcripcion
    except Exception as e:
        print(f"Error encontrado: {str(e)}")
        return None
    
def copiar_transcript(texto):
    pyperclip.copy(texto)

def main():
    while True:
        frames, frecuencia = grabar_audio()
        archivo_audio_temp = guardar(frames, frecuencia)
        print("Transcribiendo...")
        transcripcion = transcript(archivo_audio_temp) 
        if transcripcion:
            print(f"\n\nDijiste: {transcripcion}")
            print("Copiando al portapapeles...")
            print("\n\nCopiado con éxito en el portapapeles")
            copiar_transcript(transcripcion)
        else:
            print("Transcripción fallida") ##por si hay un error de lectura
        
        os.unlink(archivo_audio_temp)

if __name__=="__main__":
    main()