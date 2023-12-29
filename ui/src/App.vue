<template>
    <div class="wrapper">
        <button class="btn" @click="!recording ? start() : stop()">
            {{ !recording ? 'Start' : 'Stop' }}
        </button>
        <div class="text-holder" v-if="text || tempText">
            <span v-if="text" class="text"> {{ text }} </span>
            <span v-if="tempText" class="temp-text"> {{ tempText }} </span>
        </div>
        <div v-else class="placeholder">Text will appear here</div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

import { AudioAnalyticsSession } from '@/services/audio-analytics'
import type { AnalyticsEvent } from '@/services/audio-analytics'
import { TranscriptionResponse, TranscriptionChunk } from '@/protobufs/transcription'

class Data {
    recording = false
    session: AudioAnalyticsSession | undefined
    text = ''
    tempChunks: TranscriptionChunk[] = []
}

export default defineComponent({
    name: 'App',
    data: function () {
        return new Data()
    },
    computed: {
        tempText: function (): string {
            return this.tempChunks.map((c) => c.text).join()
        }
    },
    methods: {
        start: async function () {
            this.text = ''
            try {
                this.session = await AudioAnalyticsSession.create()
                this.session.addEventListener((e) => this.handleEvent(e))
                this.session.start()
                this.recording = true
            } catch (e) {
                console.error('Failed to start audio recording', e)
                alert('Failed to start audio recording')
            }
        },

        stop: function () {
            this.session?.stop()
            this.recording = false
        },

        handleEvent: function (event: AnalyticsEvent) {
            switch (event.kind) {
                case 'text':
                    this.decodeResponse(event.res)
                    break
                case 'error':
                    console.error('An error occured, stopping session!')
                    break
            }
        },

        decodeResponse(response: TranscriptionResponse) {
            this.finalizeChunks(response.buffer_start)
            this.tempChunks = response.chunks
        },

        finalizeChunks(before: number) {
            const finalized = this.tempChunks
                .filter((c) => c.end_time <= before)
                .map((c) => c.text)
                .join()
            this.text += finalized
        }
    }
})
</script>

<style>
* {
    box-sizing: border-box;
    font-family: sans-serif;
    font-size: 1rem;
}
</style>

<style scoped>
.wrapper {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    padding: 32px;
}

.text-holder,
.placeholder {
    margin-top: 16px;
}

.text,
.temp-text,
.placeholder {
    min-height: 12px;
}

.placeholder {
    color: gray;
}

.temp-text {
    color: rgb(152, 152, 152);
}

.btn {
    max-width: 140px;
}

.btn-holder {
    width: 100%;
    display: flex;
    flex-direction: row;
    justify-content: center;
}
</style>
