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
        class="more-info__container"
    >
        <h3 class="more-info__title">
            Citation Link
        </h3>
        <div
            v-for="item in citationArr"
            :key="item[0]"
            class="more-info__row"
        >
            <div>
                {{ item[0] }}
            </div>
            <div>
                {{ item[1] }}
            </div>
        </div>
        <div />
    </div>
</template>
