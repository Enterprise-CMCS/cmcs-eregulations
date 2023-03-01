import SupplementalContentObject from '../eregs-component-lib/src/components/SupplementalContentObject.vue';

export default {
  title: 'Supplemental Resources/Supplemental Content Object',
  component: SupplementalContentObject,
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { SupplementalContentObject },
  template: '<supplemental-content-object v-bind="$props" ></supplemental-content-object>',
});

export const Basic = Template.bind({});
Basic.args = {
  "title": "Medicaid Program; Medicaid Management Information System: Revised Definition of “Mechanized Claims Processing and Information Retrieval System” (54 FR 41966), October 13, 1989.",
  "url": "https://s3.amazonaws.com/archives.federalregister.gov/issue_slice/1989/10/13/41964-41974.pdf#page=3",
  "sections": [
    {
      "title": "42",
      "part": "433",
      "section": "111"
    },
  ]
};

export const AllFields = Template.bind({});
AllFields.args = {
  "date": "1989-10-13",
  "name": "Medicaid Management Information System",
  "description": "Medicaid Program; Medicaid Management Information System: Revised Definition of “Mechanized Claims Processing and Information Retrieval System” (54 FR 41966), October 13, 1989.",
  "url": "https://s3.amazonaws.com/archives.federalregister.gov/issue_slice/1989/10/13/41964-41974.pdf#page=3",
  "sections": [
    {
      "title": "42",
      "part": "433",
      "section": "111"
    },
  ]
};