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
                    <option value="" disabled selected>Title</option>
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
                    <option value="" disable selected>Part</option>
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
                />
                <input
                    id="jumpBtn"
                    class="submit"
                    :class="{ active: isActive }"
                    type="submit"
                    value="Go"
                />
            </div>
        </form>
    </div>
</template>
<script>
import { getTitles, getParts as fetchParts } from "utilities/api.js";

export default {
    name: "JumpTo",

    props: {
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
    },
    data() {
        return {
            titles: [],
            selectedPart: "",
            defaultTitle: "",
            selectedTitle: "",
            selectedSection: "",
            hideTitle: false,
            filteredParts: [],
            isActive: false,
            parts: [],
            link: "",
        };
    },

    async created() {
        // When title 45 or another title is added uncomment line below, and remove the hardcoded
        this.titles = await getTitles({ apiUrl: this.apiUrl });
        if (this.titles.length === 1) {
            this.selectedTitle = this.titles[0];
            this.defaultTitle = this.selectedTitle;
            this.hideTitle = true;
        }
        if (this.title !== "") {
            this.selectedTitle = this.title;
            this.hideTitle = true;
        }
        if (this.part !== "") {
            this.selectedPart = this.part;
            this.isActive = true;
        }
    },

    watch: {
        selectedTitle(title) {
            if (title === "") {
                this.selectedPart = "";
                this.isActive = false;
            } else {
                this.getParts(title);
            }
        },

        selectedPart(part) {
            if (part !== "") {
                this.isActive = true;
            } else {
                this.isActive = false;
            }
        },
    },

    methods: {
        async getParts(title) {
            const partsList = await fetchParts(title, this.apiUrl);
            // temporarily filter part 75. See EREGCSC-1397
            this.filteredParts = partsList
                .map((part) => part.name)
                .filter((part) => part !== "75");
        },
        getLink(e) {
            let link = `${this.homeUrl}goto/?title=${this.selectedTitle}&part=${this.selectedPart}`;
            if (this.selectedSection !== "") {
                link += `&section=${this.selectedSection}&-version='latest'`;
            }

            window.location.href = link;
        },
    },
};
</script>
