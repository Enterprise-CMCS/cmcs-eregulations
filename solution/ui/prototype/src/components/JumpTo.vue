<template>
    <div class="jump-to">

        <div v-if="header !== ''" class="jump-to-label">
            {{ header }}
        </div>

        <form @submit.prevent="formSubmit">
            <input name="-version" type="hidden" required value="" />
            <input name="title" type="hidden" required value="42" />

            <div class="jump-to-input">
                <select v-if="defaultTitle !== ''" name="title" class="ds-c-field" required>
                    <option value="" disabled selected>Title</option>
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
                        <option value="" disabled selected>Part</option>
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
    required: false
  },
  defaultTitle:{
      type: Number,
      required:false
  }
},

    data() {
        return {
            partNames: null,
            selectedPart: "400"
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
            this.$router.push({ name: "part", params: { title: "42", part: this.selectedPart } });
        }
    }
};
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.jump-to .dot {
    margin: 0 5px;
}
.jump-to select{
     border: 1px solid #D6D7D9;
}
.jump-to-input{
    padding:10px;
}
.jump-to input.submit {
    border: solid 1px #D6D7D9;
    color: #A3A3A3;
    background-color: white;
}
.jump-to .number-box{
    border: #D6D7D9 1px solid
}
</style>
