<template>
    <div style="margin: 15px 0px">
        <div class="supplemental-content__title">
            {{ formattedDate }}{{ supplementalContent.name ? ` | ${supplementalContent.name}`: "" }}
        </div>
        <div class="supplemental-content__text">
            {{ supplementalContent.description }}
            <a
                :href="supplementalContent.url"
                target="_blank"
            ><v-icon>mdi-open-in-new</v-icon></a>
        </div>
    </div>
</template>

<script>
export default {
  name: "SupplementalContentList",
  props: {
      supplementalContent: Object
  },
  computed: {
    formattedDate: function(){
      const date =  new Date(this.supplementalContent.updated_at)
      const options = {year: 'numeric', month: 'long', day: 'numeric' };
      return new Intl.DateTimeFormat('en-US', options).format(date)
    },
  }
}
</script>

<style >
.supplemental-content__title{
  font-size:15px;
  font-weight: bold;
  color: #046791;
}
.supplemental-content__text{
  font-size:15px;
  color: #046791;
  width: 90%
}
</style>