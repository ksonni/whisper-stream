const RecordingConfig = {
    samplingRate: 16_000,
    blobIntervalMillis: 5_000,
    mimeType: 'audio/webm;codecs=opus'
} as const

export class AudioRecordingSession {
    private recorder: MediaRecorder
    private ws?: WebSocket;
    private timer?: number;

    constructor(private stream: MediaStream) {
        this.recorder = new MediaRecorder(stream, { mimeType: RecordingConfig.mimeType })
    }

    start(handler: (event: 'error') => void) {
        this.ws = new WebSocket('ws://localhost:3000/transcribe')
        this.recorder.addEventListener('dataavailable', async (e) => {
            const buffer = await e.data.arrayBuffer();
            this.ws?.send(buffer);
        });
        this.recorder.addEventListener('error', (e) => {
            console.error('Recording failed!', e)
            handler('error')
        })
        this.recorder.start()
        this.timer = window.setInterval(
            () => this.reinitRecorder(), 
            RecordingConfig.blobIntervalMillis
        )
    }

    // This is done to produce a complete playable audio blob every couple seconds
    private reinitRecorder() {
        this.recorder.stop();
        this.recorder.start();
    }

    stop() {
        this.stream.getTracks().forEach((track) => track.stop())
        this.recorder.stop()
        this.ws?.close()
        this.ws = undefined;
        if (this.timer) {
            window.clearInterval(this.timer);
        }
    }

    static async createSession(): Promise<AudioRecordingSession> {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: { sampleRate: RecordingConfig.samplingRate }
        })
        return new AudioRecordingSession(stream)
    }
}
