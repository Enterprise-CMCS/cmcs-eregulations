<template>
    <div class="jump-to">
        <div v-if="header !== ''" class="jump-to-label">
            {{ header }}
        </div>

        <form @submit.prevent="formSubmit">
            <input name="-version" type="hidden" required value="" />

            <div class="jump-to-input">
                <select
                    v-if="defaultTitle !== ''"
                    name="title"
                    class="ds-c-field"
                    required
                    v-model="selectedTitle"
                >
                    <option value="" disabled selected>Title</option>
                    <option value="42">42</option>
                </select>
                §
                <select
                    name="part"
                    class="ds-c-field"
                    aria-label="Regulation part number"
                    v-model="selectedPart"
                    required
                >
                    <template v-if="partNames">
                        <option value="" disable selected>Part</option>
                        <option
                            v-for="partName in partNames"
                            :value="partName"
                            :key="partName"
                        >
                            {{ partName }}
                        </option>
                    </template>
                </select>
                <span class="dot">.</span>
                <input
                    class="number-box ds-c-field"
                    name="section"
                    placeholder=""
                    type="text"
                    pattern="\d+"
                    title="Regulation section number, i.e. 111"
                    aria-label="Regulation section number, i.e. 111"
                />
            </div>

            <input class="submit" type="submit" value="Go" />
        </form>
    </div>
</template>

<script>
import { getPartNames } from "@/utilities/api";

export default {
    name: "JumpTo",
    props: {
        header: {
            type: String,
            required: false,
        },
        defaultTitle: {
            type: Number,
            required: false,
        },
    },

    data() {
        return {
            partNames: null,
            selectedPart: "",
            selectedTitle: "",
        };
    },

    async created() {
        try {
            this.partNames = await getPartNames();
        } catch (error) {
            console.error(error);
        }
    },

    methods: {
        formSubmit() {
            this.$router.push({
                name: "part",
                params: { title: this.selectedTitle, part: this.selectedPart },
            });
        },
    },
};
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.jump-to .dot {
    margin: 0 5px;
}

.jump-to .jump-to-input select {
    
    border: #d6d7d9 1px solid;
}
.jump-to-input {
    padding: 10px;
}

.jump-to input.submit {
    border: solid 1px #d6d7d9;
    color: #a3a3a3;
    background-color: white;
}

.jump-to .number-box {
    border: #d6d7d9 1px solid;
}
</style>
