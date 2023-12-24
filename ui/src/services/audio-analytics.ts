const Config = {
    // Sampling rate of the audio
    samplingRate: 16_000,
    // Duration of silence needed for request to be sent to server
    minSilenceInterval: 1000,
    // The longest duration we can wait before making a request
    maxSplitInterval: 15_000,
    // Recording mime type
    mimeType: 'audio/webm;codecs=opus',
    // Minimum threshold for sound to possibly be considered speech
    minSpeakingAmplitude: -45,
    // WebSocket to send samples for analysis
    wsUrl: 'ws://localhost:3000/transcribe'
} as const

export class AudioAnalyticsSession {
    private recorder: MediaRecorder
    private ws?: WebSocket
    private timer?: number
    private detectSpeechLoop?: number
    private audioContext = new AudioContext()
    private source: MediaStreamAudioSourceNode
    private analyzer: AnalyserNode
    private domainData: Uint8Array
    private lastSpeechTime?: number
    private lastInitTime?: number
    private speechPresentInSample = false

    constructor(private stream: MediaStream) {
        this.recorder = new MediaRecorder(stream, { mimeType: Config.mimeType })
        this.source = this.audioContext.createMediaStreamSource(this.stream)
        this.analyzer = this.audioContext.createAnalyser()
        this.analyzer.minDecibels = Config.minSpeakingAmplitude
        this.source.connect(this.analyzer)
        this.domainData = new Uint8Array(this.analyzer.frequencyBinCount)
    }

    start(handler: (event: 'error') => void) {
        this.ws = new WebSocket(Config.wsUrl)
        this.recorder.addEventListener('dataavailable', async (e) => {
            if (!this.speechPresentInSample) {
                return
            }
            this.speechPresentInSample = false
            const buffer = await e.data.arrayBuffer()
            this.ws?.send(buffer)
        })
        this.recorder.addEventListener('error', (e) => {
            console.error('Recording failed', e)
            handler('error')
        })
        this.lastInitTime = Date.now()
        this.recorder.start()

        const detectSpeech = () => {
            this.analyzer.getByteFrequencyData(this.domainData)

            // TODO: be more selective about human voice frequency?
            const speaking = this.domainData.some((data) => data > 0)

            if (speaking) {
                this.speechPresentInSample = true
                this.lastSpeechTime = Date.now()
            }
            const now = Date.now()

            const silentForLongEnough =
                !speaking &&
                this.lastSpeechTime &&
                now - this.lastSpeechTime >= Config.minSilenceInterval

            const recordingTooLong =
                this.lastInitTime && now - this.lastInitTime >= Config.maxSplitInterval

            if (silentForLongEnough || recordingTooLong) {
                this.lastSpeechTime = undefined
                this.reinitRecorder()
            }
            this.detectSpeechLoop = window.requestAnimationFrame(detectSpeech)
        }
        this.detectSpeechLoop = window.requestAnimationFrame(detectSpeech)
    }

    stop() {
        this.stream.getTracks().forEach((track) => track.stop())
        this.recorder.stop()
        this.ws?.close()
        this.ws = undefined
        if (this.timer) {
            window.clearInterval(this.timer)
        }
        if (this.detectSpeechLoop) {
            window.cancelAnimationFrame(this.detectSpeechLoop)
        }
    }

    // This finalizes a sample which makes it ready for analysis
    private reinitRecorder() {
        this.recorder.stop()
        this.recorder.start()
        this.lastInitTime = Date.now()
    }

    static async create(): Promise<AudioAnalyticsSession> {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: { sampleRate: Config.samplingRate }
        })
        return new AudioAnalyticsSession(stream)
    }
}
