<template>
    <div class="subchapter">
        <h2>{{ label }}</h2>
        <template v-for="part in partsArr">
            <div class="part-names" :key="part[0]">
                <router-link :to="{ name: 'about' }">
                    <span class="part-number">Part {{ part[0] }} </span>
                    <span>–</span>
                    <span class="part-title"> {{ part[1].description }}</span>
                </router-link>
            </div>
        </template>
    </div>
</template>

<script>
export default {
    name: "TocSubchapter",

    props: {
        label: {
            type: String,
            required: true
        },
        parts: {
            type: Object,
            required: false
        }
    },

    computed: {
        partsArr() {
            console.log(this.parts);
            return Object.entries(this.parts);
        }
    }

}
</script>

<style>

</style>

