<template>
<div>
    <div class="jump-to-label">Jump to Regulation Section</div>
    <div class="form">
        <div class="jump-to-input">
            <select
                v-if="defaultTitle === ''"
                v-model="selectedTitle"
                name="title"
                class="ds-c-field"
                required
            >
                <option value="" disabled selected>Title</option>
                    <option
                        v-for="title in titles"
                        :key=title
                        :value=title
                    >
                        {{ title }} CFR
                    </option>
            </select>
                §
            <select
                v-model="selectedPart"
                name="part"
                class="ds-c-field"
                aria-label="Regulation part number"
                required
                :disabled="!selectedTitle"
            >
                <option value="" disable selected>Part</option>
                <option
                    v-for="part in filteredParts"
                    :key=part
                    :value=part
                >
                    {{ part }}
                </option>
            </select>
            <span class="dot">.</span>
            <input
                v-model="selectedSection"
                class="number-box ds-c-field"
                name="section"
                placeholder=""
                type="text"
                pattern="\d+"
                title="Regulation section number, i.e. 111"
                aria-label="Regulation section number, i.e. 111"
            />
        </div>
        <input class="submit" :class="{active: isActive}" type="submit" value="Go" @click="getLink" /></div>

</div>
</template>
<script>

import { getTitles, getParts } from "../api";

export default {
    name: "JumpTo",

    props: {
        apiurl: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            required: false,
            default: ""
        },
        part: {
            type: String,
            required: false,
            default: ""
        },
    },
    data() {
        return {
            partNames: null,
            titles: [],
            selectedPart: "",
            defaultTitle:'',
            selectedTitle: "",
            selectedSection: "",
            hideTitle: false,
            filteredParts:[],
            isActive: false,
            parts:[],
            link: "",
        };
    },

    async created() {
        this.titles = await getTitles(this.apiurl);
        if(this.titles.length === 1){
            this.selectedTitle = this.titles[0];
            this.defaultTitle = this.selectedTitle;
            this.hideTitle= true;
        }
        if(this.title!==""){
            this.selectedTitle=this.title;
            this.hideTitle=true;
        }
        if(this.part !==""){
            this.selectedPart=this.part;
            this.isActive=true;
        }
    },

    watch:{
        selectedTitle(title) {
            if(title === ""){
                this.selectedPart=""
                this.isActive=false;
            }
            else{
                this.getParts(title)
            }
        },
    
        selectedPart(part) {
            if(part !== ""){
                this.isActive=true;
            }
            else{
                this.isActive=false;
            }
        }
    },

    methods: {
        async getParts(title) {
            const partsList = await getParts(this.apiurl, title)
            this.filteredParts = partsList.map((part) => part.name);
        },
        getLink(){
            if(this.isActive){
                const link = `/${this.selectedTitle}/${this.selectedPart}/${this.selectedSection}`
                window.location.href = link
            }
        }
    }    
};
</script>
