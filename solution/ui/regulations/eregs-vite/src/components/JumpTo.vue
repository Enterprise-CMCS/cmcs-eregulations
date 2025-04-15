<script setup>
import { ref, watch, onMounted } from "vue";
import { getTitles, getParts as fetchParts } from "utilities/api.js";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
    title: {
        type: String,
        required: false,
        default: "",
    },
    part: {
        type: String,
        required: false,
        default: "",
    },
    homeUrl: {
        type: String,
        default: "/",
    },
});

const titles = ref([]);
const selectedPart = ref("");
const defaultTitle = ref("");
const selectedTitle = ref("");
const selectedSection = ref("");
const hideTitle = ref(false);
const filteredParts = ref([]);
const isActive = ref(false);

const getParts = async (title) => {
    const partsList = await fetchParts({ title, apiUrl: props.apiUrl });
    filteredParts.value = partsList
        .map((part) => part.name)
        .filter((part) => part !== "75");
};

const getLink = () => {
    let linkValue = `${props.homeUrl}goto/?title=${selectedTitle.value}&part=${selectedPart.value}`;
    if (selectedSection.value !== "") {
        linkValue += `&section=${selectedSection.value}&-version='latest'`;
    }
    window.location.href = linkValue;
};

onMounted(async () => {
    titles.value = await getTitles({ apiUrl: props.apiUrl });
    if (titles.value.length === 1) {
        selectedTitle.value = titles.value[0];
        defaultTitle.value = selectedTitle.value;
        hideTitle.value = true;
    }
    if (props.title !== "") {
        selectedTitle.value = props.title;
        hideTitle.value = true;
    }
    if (props.part !== "") {
        selectedPart.value = props.part;
        isActive.value = true;
    }
});

watch(selectedTitle, (title) => {
    if (title === "") {
        selectedPart.value = "";
        isActive.value = false;
    } else {
        getParts(title);
    }
});

watch(selectedPart, (part) => {
    isActive.value = part !== "";
});
</script>

<template>
    <div>
        <form @submit.prevent="getLink">
            <div class="jump-to-input">
                <select
                    v-if="defaultTitle === ''"
                    id="jumpToTitle"
                    v-model="selectedTitle"
                    name="title"
                    aria-label="Regulation title number"
                    class="ds-c-field"
                    required
                >
                    <option
                        value=""
                        disabled
                        selected
                    >
                        Title
                    </option>
                    <option
                        v-for="listedTitle in titles"
                        :key="listedTitle"
                        :value="listedTitle"
                    >
                        {{ listedTitle }} CFR
                    </option>
                </select>
                <span class="section-symbol">§</span>
                <select
                    id="jumpToPart"
                    v-model="selectedPart"
                    name="part"
                    class="ds-c-field"
                    aria-label="Regulation part number"
                    required
                    :disabled="!selectedTitle"
                >
                    <option
                        value=""
                        disable
                        selected
                    >
                        Part
                    </option>
                    <option
                        v-for="listedPart in filteredParts"
                        :key="listedPart"
                        :value="listedPart"
                    >
                        {{ listedPart }}
                    </option>
                </select>
                <span class="dot">.</span>
                <input
                    id="jumpToSection"
                    v-model="selectedSection"
                    class="number-box ds-c-field"
                    name="section"
                    placeholder=""
                    type="text"
                    pattern="\d+"
                    title="Regulation section number, i.e. 111"
                    aria-label="Regulation section number, i.e. 111"
                >
                <input
                    id="jumpBtn"
                    class="submit"
                    :class="{ active: isActive }"
                    type="submit"
                    value="Go"
                >
            </div>
        </form>
    </div>
</template>
