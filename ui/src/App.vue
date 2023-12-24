<template>
    <header>
        <div class="wrapper">
            <button @click="!recording ? start() : stop()">
                {{ !recording ? 'Start' : 'Stop' }}
            </button>
        </div>
    </header>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

import { AudioAnalyticsSession } from '@/services/audio-analytics'

class Data {
    recording = false
    session: AudioAnalyticsSession | undefined
}

export default defineComponent({
    name: 'App',
    data: function () {
        return new Data()
    },
    methods: {
        start: async function () {
            try {
                this.session = await AudioAnalyticsSession.create()
                this.session.start((e) => {
                    if (e === 'error') {
                        this.stop()
                    }
                })
                this.recording = true
            } catch (e) {
                console.error('Failed to start audio recording', e)
                alert('Failed to start audio recording')
            }
        },

        stop: function () {
            this.session?.stop()
            this.recording = false
        }
    }
})
</script>

<style scoped></style>
