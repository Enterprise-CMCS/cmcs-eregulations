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
const filteredParts = ref([]);

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

    if (props.title !== "") {
        selectedTitle.value = props.title;
    } else {
        selectedTitle.value = titles.value[0];
        defaultTitle.value = selectedTitle.value;
    }

    if (props.part !== "") {
        selectedPart.value = props.part;
    }
});

watch(selectedTitle, (title) => {
    if (title === "") {
        selectedPart.value = "";
    } else {
        getParts(title);
    }
});
</script>

<template>
    <div>
        <form @submit.prevent="getLink">
            <div class="jump-to-input">
                <select
                    id="jumpToTitle"
                    v-model="selectedTitle"
                    name="title"
                    aria-label="Regulation title number"
                    class="ds-c-field"
                    :disabled="!selectedTitle"
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
                    :disabled="!selectedTitle || filteredParts.length === 0"
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
                    :disabled="!selectedTitle"
                >
                <input
                    id="jumpBtn"
                    class="submit active"
                    :disabled="!selectedTitle"
                    type="submit"
                    value="Go"
                >
            </div>
        </form>
    </div>
</template>
