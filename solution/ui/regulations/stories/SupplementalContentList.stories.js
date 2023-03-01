import SupplementalContentList from '../eregs-component-lib/src/components/SupplementalContentList.vue';

export default {
  title: 'Supplemental Resources/Supplemental Content List',
  component: SupplementalContentList,
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { SupplementalContentList },
  template: '<supplemental-content-list v-bind="$props" ></supplemental-content-list>',
});

export const Basic = Template.bind({});
Basic.args = {
  "supplemental_content": [
    {
      "name": "Medicaid Program; Medicaid Management Information System: Revised Definition of “Mechanized Claims Processing and Information Retrieval System” (54 FR 41966), October 13, 1989.",
      "url": "https://s3.amazonaws.com/archives.federalregister.gov/issue_slice/1989/10/13/41964-41974.pdf#page=3",
      "sections": [
       {
        "title": "42",
        "part": "433",
        "section": "111"
       },
       {
        "title": "42",
        "part": "433",
        "section": "112"
       },
       {
        "title": "42",
        "part": "433",
        "section": "114"
       },
       {
        "title": "42",
        "part": "433",
        "section": "119"
       },
       {
        "title": "42",
        "part": "433",
        "section": "120"
       },
       {
        "title": "42",
        "part": "433",
        "section": "121"
       },
       {
        "title": "42",
        "part": "433",
        "section": "122"
       },
       {
        "title": "42",
        "part": "433",
        "section": "130"
       },
       {
        "title": "42",
        "part": "433",
        "section": "131"
       }
      ]
     },
     {
      "name": "Medicaid Program; Mechanized Claims Processing and Information Retrieval Systems (90/10) (80 FR 75817), December 4, 2015",
      "url": "https://www.federalregister.gov/documents/2015/12/04/2015-30591/medicaid-program-mechanized-claims-processing-and-information-retrieval-systems-9010",
      "sections": [
       {
        "title": "42",
        "part": "433",
        "section": "110"
       },
       {
        "title": "42",
        "part": "433",
        "section": "111"
       },
       {
        "title": "42",
        "part": "433",
        "section": "112"
       },
       {
        "title": "42",
        "part": "433",
        "section": "116"
       },
       {
        "title": "42",
        "part": "433",
        "section": "119"
       },
       {
        "title": "42",
        "part": "433",
        "section": "120"
       }
      ]
     },
  ]
};