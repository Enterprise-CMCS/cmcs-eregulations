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
                    <option v-for="title in this.titles" :value="title">{{ title }}</option>
                </select>
                §
                <select
                    name="part"
                    class="ds-c-field"
                    aria-label="Regulation part number"
                    v-model="selectedPart"
                    required
                    :disabled="!partNames"
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
                    v-model="selectedSection"
                    pattern="\d+"
                    title="Regulation section number, i.e. 111"
                    aria-label="Regulation section number, i.e. 111"
                />
            </div>

            <input class="submit" v-bind:class="{active: isActive}" type="submit" value="Go" />
        </form>
    </div>
</template>

<script>
import {getTOC, getPartNames, getPartTOC} from "@/utilities/api";
import {flattenSubpart} from "@/utilities/utils";

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
            titles: [],
            selectedPart: "",
            selectedTitle: "",
            selectedSection: "",
        };
    },
    watch :{
      async selectedTitle(newTitle) {
        console.log(newTitle)
        this.partNames = await getPartNames(newTitle);
      }
    },

    async created() {
        try {
            const toc = await getTOC()
            this.titles = toc.map(title => title.identifier[0])

        } catch (error) {
            console.error(error);
        }
    },
    computed: {
      isActive(){
        return this.selectedTitle && this.selectedPart
      }
    },
    methods: {
        async formSubmit() {
            const resourcesDisplay = window.location.pathname.indexOf('sidebar') >= 0 ? "sidebar" : "drawer"
            let urlParams = {
                title: this.selectedTitle,
                part: this.selectedPart,
            };
            let name = window.location.pathname.indexOf('zoom') >= 0 ? "PDpart" : "part"
            const partToc = await getPartTOC(this.selectedTitle, this.selectedPart)
            let subpart
            const orphans = partToc.children.filter( child => child.type === "section"
                  && child.identifier[0] === this.selectedPart
                  && child.identifier[1] === this.selectedSection
            )
            if (!orphans.length){
              // keep looking
              // also, reserved subparts have no children or descendant range.
              subpart =  partToc.children.filter( child => child.type === "subpart" && child.reserved === false)
              .find( sp =>
                  Number(sp.descendant_range[0].split(".")[1]) <= this.selectedSection
                  && Number(sp.descendant_range[1].split(".")[1]) >= this.selectedSection
              )

              if (subpart){
                  const flatSubpart = flattenSubpart(subpart)
                  const section = flatSubpart.children.find(section => section.identifier[1] === this.selectedSection)
                  subpart = flatSubpart.identifier[0]
                  if (!section){
                      this.selectedSection = undefined
                  }
              }

            }

            if(name === "PDpart"){
                if (this.selectedSection) {
                    name = "PDpart-section"
                    urlParams.section = this.selectedSection
                    if (subpart) {
                      urlParams.subPart = `Subpart-${subpart}`
                    } else {
                      urlParams.subPart = "Subpart-undefined"
                    }
                }
                this.$router.push({
                    name,
                    params:{
                      ...urlParams,
                      resourcesDisplay
                    }
                })
            }
            else{
                const query = {}
                let tab = "part"
                if (this.selectedSection) {
                    tab = "section"
                    query.section = this.selectedSection
                    if (subpart) {
                      query.subpart = subpart
                    }
                }
                this.$router.push({
                    name: this.navName,
                    params: {
                        ...urlParams,
                        tab,
                        resourcesDisplay
                    },
                    query,
                });
            }
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

.jump-to input.submit.active {
    border: solid 1px #046791;
    color: #FFFFFF;
    background-color: #046791;
}

.jump-to .number-box {
    border: #d6d7d9 1px solid;
}
</style>
