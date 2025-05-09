// This is in JS because of web worker stuff
export default class AudioRecorder extends AudioWorkletProcessor {
    static get parameterDescriptors() {
        return []
    }
    process(inputs: any) {
        // Only need in channel
        const input = inputs?.[0]?.[0]
        if (input) {
            this.port.postMessage(input)
        }
        return true
    }
}
registerProcessor('audio-recorder', AudioRecorder)
