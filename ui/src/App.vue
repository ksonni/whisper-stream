<template>
    <div class="wrapper">
        <button class="btn" @click="!recording ? start() : stop()">
            {{ !recording ? 'Start' : 'Stop' }}
        </button>
        <div v-if="text" class="text">{{ text }}</div>
        <div v-else class="placeholder">Text will appear here</div>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

import { AudioAnalyticsSession } from '@/services/audio-analytics'
import type { AnalyticsEvent } from '@/services/audio-analytics'

class Data {
    recording = false
    session: AudioAnalyticsSession | undefined
    text = ''
}

export default defineComponent({
    name: 'App',
    data: function () {
        return new Data()
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
            console.log('Got an anlytics event', event)
            switch (event.kind) {
                case 'text':
                    this.text = event.text
                    break
                case 'error':
                    break
            }
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

.text,
.placeholder {
    margin-top: 16px;
    min-height: 12px;
}

.placeholder {
    color: gray;
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
