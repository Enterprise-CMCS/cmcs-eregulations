<script setup>
import { computed } from "vue";

const props = defineProps({
    citationObj: {
        type: Object,
        required: true,
    },
});

const citationArr = computed(() => Object.entries(props.citationObj));
</script>

<template>
    <div
        v-if="citationArr.length"
        class="research__container"
    >
        <h3 class="research__title">
            Citation Link
        </h3>
        <div
            v-for="item in citationArr"
            :key="item[0]"
            class="research__row"
        >
            {{ item[1] }}
        </div>
    </div>
</template>
