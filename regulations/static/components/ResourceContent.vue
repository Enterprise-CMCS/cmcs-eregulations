<template>
  <div>
    <div>
      <h2>Filter Resources</h2>
      <label for="part">Part</label>
      <select id="part" v-model="part" v-on:change="getSubParts">
        <option disabled value="">Select Part</option>
        <option v-for="partOption in partOptions" v-bind:value="partOption.part">{{partOption.part}}</option>
      </select>
      <label v-if="part" for="subPart">SubPart</label>
      <select v-if="part" id="subPart" v-model="subPart" v-on:change="getSections">
        <option value="">Select Subpart</option>
        <option value="ORPHAN">No Subpart</option>
        <option v-for="subPartOption in subPartOptions" v-bind:value="subPartOption.id">Subpart {{subPartOption.subpart_id}}</option>
      </select>
      <label v-if="part" for="section">Section</label>
      <select v-if="part" id="section" v-model="section">
        <option value="">Select Section</option>
        <option v-for="sectionOption in sectionOptions" v-bind:value="sectionOption.id">Section {{sectionOption.section_id}}</option>

      </select>
      <label for="resourceCategory">Resource Category</label>
      <select id="resourceCategory" v-model="category">
        <option disabled value="">Select Category</option>
        <option v-for="categoryOption in categoryOptions" v-bind:value="categoryOption.id">{{categoryOption.name}}</option>
      </select>

      <button v-if="section" v-on:click="setSection(section, `${title} ${part}.${sectionOptions.find(ss => ss.id == section).section_id}`)">
        Fetch Supplemental Content
      </button>
    </div>

    <div>
      <ul>
        <li>Selected Part: {{ part }}</li>
        <li>Selected SubPart: {{ subPart }}</li>
        <li>Selected Section: {{ section }}</li>
        <li>Selected Category: {{ category }}</li>
        <li>Supplemental Content Count: {{ supplementalContent.length }}</li>
        <li>History: <button v-for="h in history" @click="setSection(h.id)">{{h.name}}</button></li>
      </ul>


        <div v-for="content in supplementalContent">
          <span style="background-color: darkgrey">{{content.category}}</span>
          <br/>
          <a :href="content.url" target="_blank">{{content.description || content.name}}</a>
          <br/>
          SECTIONS:
          <span
              style="font-size: 12px; color:#046791"
              v-for="location in content.locations"
          >
            <button @click="setSection(location.id, location.name)">
              {{location.name}}
            </button>

          </span>
        </div>


    </div>

  </div>
</template>

<script>
export default {
  props: {
    api_url: {
        type: String,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
  },
  data: function(){
    return {
      part: '',
      partOptions: [{part:"Loading"}],
      subPart: '',
      subPartOptions:  [{subpart_id:"Loading"}],
      section:'',
      sectionOptions:  [{section_id:"Loading"}],
      category:'',
      categoryOptions: [{category:"Loading"}],
      supplementalContent:[],
      history:[]
    }
  },
  created: function(){
    this.getParts(this.title)
    this.getCategories()
  },
  methods:{
    async getParts(title){
      console.log(title)
      try {
        const response = await fetch(
            `${this.api_url}api/title/${title}/parts`
        );
        const content = await response.json();
        console.log(content)
        this.partOptions = content;
      } catch (error) {
          console.error(error);
      }
    },
    async getSubParts(){
      await this.getSections()
      try {
       const response = await fetch(
            `${this.api_url}api/title/${this.title}/part/${this.part}/subParts`
        );
        const content = await response.json();
        console.log(content)
        this.subPartOptions = content;
      } catch (error) {
          console.error(error);
      }
    },
    async getSections(){
      try {
        const url = this.subPart ?
              `${this.api_url}api/title/${this.title}/part/${this.part}/subPart/${this.subPart}/sections`
            :
              `${this.api_url}api/title/${this.title}/part/${this.part}/sections`
        const response = await fetch(url);
        const content = await response.json();
        this.sectionOptions = content;
      } catch (error) {
          console.error(error);
      }
    },
    async getCategories(){
      try {
        const response = await fetch(
            `${this.api_url}api/categories/`
        );
        const content = await response.json();
        console.log(content)
        this.categoryOptions = content;
      } catch (error) {
          console.error(error);
      }
    },
    async getSupplementalContent(){
      try {
        var url = `${this.api_url}api/supplementalContent?section=${this.section}`
        if (this.category) {
          url = `${url}&category=${this.category}`
        }
        const response = await fetch(url);
        const content = await response.json();
        console.log(content)
        this.supplementalContent = content;
      } catch (error) {
          console.error(error);
      }
    },
    async setSection(id, name){
      this.history.push({name, id})
      this.section = id
      await this.getSupplementalContent()
    },
  }
}
</script>
