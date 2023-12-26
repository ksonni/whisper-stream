import { v4 as uuid } from 'uuid'
import { TranscriptionRequest, TranscriptionResult } from '@/protobufs/transcription'
import workerUrl from './audio-recorder-worklet.js?worker&url'

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
    private ws?: WebSocket
    private timer?: number
    private detectSpeechLoop?: number
    private source: MediaStreamAudioSourceNode
    private eventListeners: Record<string, AnalyticsEventListener> = {}

    constructor(
        private stream: MediaStream,
        private audioContext: AudioContext
    ) {
        this.source = this.audioContext.createMediaStreamSource(this.stream)
    }

    start() {
        this.ws = new WebSocket(Config.wsUrl)
        this.ws.binaryType = 'arraybuffer'
        this.ws.onmessage = (msg) => {
            const data = TranscriptionResult.deserialize(new Uint8Array(msg.data))
            if (data.code === 200) {
                const text = data.chunks.map((c) => c.text).join()
                this.dispatchEvent({ kind: 'text', text })
            } else {
                this.dispatchEvent({ kind: 'error' })
            }
        }
        this.ws.onerror = (e) => {
            console.error('Websocket error!', e)
            this.dispatchEvent({ kind: 'error' })
        }
        const node = new AudioWorkletNode(this.audioContext, 'audio-recorder')
        node.port.onmessage = (e) => {
            const data = e?.data as Float32Array
            if (!data) {
                return
            }
            if (this.ws?.readyState !== WebSocket.OPEN) {
                return
            }
            const request = TranscriptionRequest.fromObject({
                data: Array.from(data)
            })
            this.ws?.send(request.serialize())
        }
        this.source.connect(node).connect(this.audioContext.destination)
    }

    stop() {
        this.stream.getTracks().forEach((track) => track.stop())
        this.audioContext.close()
        this.source?.disconnect()
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

    static async create(): Promise<AudioAnalyticsSession> {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: { sampleRate: Config.samplingRate }
        })
        const audioContext = new AudioContext({ sampleRate: Config.samplingRate })
        await audioContext.audioWorklet.addModule(workerUrl)
        return new AudioAnalyticsSession(stream, audioContext)
    }
}
