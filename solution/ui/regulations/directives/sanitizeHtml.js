import DOMPurify from "dompurify";

// https://vuejs.org/guide/reusability/custom-directives#function-shorthand
// It's common for a custom directive to have the same behavior for mounted and updated,
// with no need for the other hooks. In such cases we can define the directive as a function:
const SanitizeHtml = (el, binding) => {
    el.innerHTML = DOMPurify.sanitize(binding.value);
};

export default SanitizeHtml;
