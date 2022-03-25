<template>
    <div>
        <div
            v-for="f in supplemental_content"
            class="card"
        >
            <SectionCard :f="f"/>
        </div>
    </div>
</template>

<script>

import SectionCard from "./SectionCard";
export default {
    name: "SectionCards",
  components: {SectionCard},
  props: {
        title: { type: String },
        part: { type: String },
        supList: {type: Array},
    },
    data: () => ({
        show: false,
    }),
    computed: {
      supplemental_content(){
        const content = []
        this.supList.forEach( category => {
              category
                  .supplemental_content
                  .map(c => {
                    c.category = category.name
                    return c
                  })
                  .forEach(c => content.push(c));
              category
                  .sub_categories.forEach( subCategory => {
                    subCategory
                    .supplemental_content
                    .map(c => {
                      c.category = subCategory.name
                      return c
                    })
                    .forEach(c => content.push(c))
              })
            })
        return content
      }
    },
    methods:{
      toggleLocations(f){
        this.show = this.show === f.url ? "":f.url
      },
    }
};
</script>

<style >
.theme--light.v-card > .v-card__subtitle {
    font-size: 11px;
    font-weight: bold;
    color: #102e43;
}
.theme--light.v-card > .v-card__text {
    color: #046791;
}
.v-btn > .v-btn__content {
    font-size: 12px;
}
.v-card__text {
    width: 95%;
}
.card{
    padding-bottom: 10px;
}
</style>