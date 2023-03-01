import SupplementalContentCategory from '../eregs-component-lib/src/components/SupplementalContentCategory.vue';

export default {
  title: 'Supplemental Resources/Supplemental Content Category',
  component: SupplementalContentCategory,
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { SupplementalContentCategory },
  template: '<supplemental-content-category v-bind="$props" ></supplemental-content-category>',
});

export const Basic = Template.bind({});
Basic.args = {
  "name": "Category A",
  "description": "Supplemental content example category A",
  "supplemental_content": [
    {
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
      ]
     },
  ],
  "sub_categories": [
    {
      "name": "Sub-category A-A",
      "description": "Example supplemental content sub-category A-A",
      "supplemental_content": [
        {
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
        },
        {
          "name": "Supplemental content example 2",
          "url": "example2",
          "sections": [
            {
              "title": "42",
              "part": "433",
              "section": "120",
            }
          ],
        },
      ],
      "sub_categories": [],
    },
    {
      "name": "Sub-category A-B",
      "description": "Example supplemental content sub-category A-B",
      "supplemental_content": [
        {
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
        },
        {
          "name": "Supplemental content example 4",
          "url": "example4",
          "sections": [
            {
              "title": "42",
              "part": "433",
              "section": "140",
            }
          ],
        },
      ],
      "sub_categories": [],
    },
  ],
};