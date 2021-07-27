import SupplementaryContent from '../components/SupplementaryContent.vue';

export default {
  title: 'SupplementaryContent/SupplementaryContent',
  component: SupplementaryContent,
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { SupplementaryContent },
  template: '<supplementary-content v-bind="$props" ></supplementary-content>',
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
  "title": "Medicaid Management Information System",
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