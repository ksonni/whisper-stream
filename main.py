import whisper

model = whisper.load_model("base")
whisper.load_audio()
result = model.transcribe("/Users/keshav/Desktop/sample.mp3")
print(result["text"])
