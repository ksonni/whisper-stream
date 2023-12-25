API_TARGET=../api/src/protobufs
UI_TARGET=../ui/src/protobufs

install:
	npm i
	rm -rf $(API_TARGET) && mkdir $(API_TARGET) 
	rm -rf $(UI_TARGET) && mkdir $(UI_TARGET)
	protoc --python_out=pyi_out:$(API_TARGET) --ts_out=$(UI_TARGET) ./transcription.proto
