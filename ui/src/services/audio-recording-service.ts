const RecordingConfig = {
    samplingRate: 16_000,
    blobIntervalMillis: 1000,
    mimeType: 'audio/webm;codecs=opus'
} as const

export class AudioRecordingSession {
    private recorder: MediaRecorder

    constructor(private stream: MediaStream) {
        this.recorder = new MediaRecorder(stream, { mimeType: RecordingConfig.mimeType })
    }

    start(handler: (event: 'error') => void) {
        this.recorder.addEventListener('dataavailable', (e) => {
            console.log('Got data', e.data)
        })
        this.recorder.addEventListener('error', (e) => {
            console.error('Recording failed!', e)
            handler('error')
        })
        this.recorder.start(RecordingConfig.blobIntervalMillis)
    }

    stop() {
        this.stream.getTracks().forEach((track) => track.stop())
        this.recorder.stop()
    }

    static async createSession(): Promise<AudioRecordingSession> {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: { sampleRate: RecordingConfig.samplingRate }
        })
        return new AudioRecordingSession(stream)
    }
}
