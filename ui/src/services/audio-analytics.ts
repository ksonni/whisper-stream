import { v4 as uuid } from 'uuid'
import { TranscriptionRequest, TranscriptionResponse } from '@/protobufs/transcription'

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

export type AnalyticsEvent =
    | { kind: 'error' }
    | {
          kind: 'text'
          text: string
      }

export type AnalyticsEventListener = (e: AnalyticsEvent) => void

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
    private eventListeners: Record<string, AnalyticsEventListener> = {}
    private packetSerial = 0

    constructor(private stream: MediaStream) {
        this.recorder = new MediaRecorder(stream, { mimeType: Config.mimeType })
        this.source = this.audioContext.createMediaStreamSource(this.stream)
        this.analyzer = this.audioContext.createAnalyser()
        this.analyzer.minDecibels = Config.minSpeakingAmplitude
        this.source.connect(this.analyzer)
        this.domainData = new Uint8Array(this.analyzer.frequencyBinCount)
    }

    start() {
        this.ws = new WebSocket(Config.wsUrl)
        this.ws.binaryType = 'arraybuffer'

        this.recorder.addEventListener('dataavailable', async (e) => {
            if (!this.speechPresentInSample) {
                return
            }
            this.speechPresentInSample = false
            const buffer = await e.data.arrayBuffer()
            this.packetSerial += 1
            const request = TranscriptionRequest.fromObject({
                serial: this.packetSerial,
                data: new Uint8Array(buffer)
            })
            this.ws?.send(request.serialize())
        })
        this.recorder.addEventListener('error', (e) => {
            console.error('Recording failed', e)
            this.dispatchEvent({ kind: 'error' })
        })
        this.lastInitTime = Date.now()
        this.recorder.start()
        this.ws.onmessage = (msg) => {
            const data = TranscriptionResponse.deserialize(new Uint8Array(msg.data))
            if (data.code === 200) {
                this.dispatchEvent({ kind: 'text', text: data.text })
            } else {
                this.dispatchEvent({ kind: 'error' })
            }
        }
        this.ws.onerror = (e) => {
            console.error('Websocket error!', e)
            this.dispatchEvent({ kind: 'error' })
        }

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

    addEventListener(listener: AnalyticsEventListener): string {
        const id = uuid()
        this.eventListeners[id] = listener
        return id
    }

    removeEventListener(id: string) {
        delete this.eventListeners[id]
    }

    private dispatchEvent(e: AnalyticsEvent) {
        Object.values(this.eventListeners).forEach((cb) => cb(e))
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
