const RecordingConfig = {
    samplingRate: 16_000,
    blobIntervalMillis: 1000,
    mimeType: 'audio/webm;codecs=opus'
} as const

export class AudioRecordingSession {
    private recorder: MediaRecorder
    private ws: WebSocket;

    constructor(private stream: MediaStream) {
        this.recorder = new MediaRecorder(stream, { mimeType: RecordingConfig.mimeType })
        this.ws = new WebSocket('ws://localhost:3000')
        this.ws.onopen = (e) => {
            this.ws.send('ping!!!');
        }
    }

    start(handler: (event: 'error') => void) {
        this.recorder.addEventListener('dataavailable', async (e) => {
            const buffer = await e.data.arrayBuffer();
            this.ws.send(buffer);
        });
        this.recorder.addEventListener('error', (e) => {
            console.error('Recording failed!', e)
            handler('error')
        })
        this.recorder.start(RecordingConfig.blobIntervalMillis)
    }

    stop() {
        this.stream.getTracks().forEach((track) => track.stop())
        this.recorder.stop()
        this.ws.close()
    }

    static async createSession(): Promise<AudioRecordingSession> {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: { sampleRate: RecordingConfig.samplingRate }
        })
        return new AudioRecordingSession(stream)
    }
}
