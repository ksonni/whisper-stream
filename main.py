import whisper

model = whisper.load_model("base")
result = model.transcribe("/Users/keshav/Desktop/sample.mp3")
print(result["text"])
