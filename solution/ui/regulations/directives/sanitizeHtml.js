import DOMPurify from "dompurify";

DOMPurify.addHook("afterSanitizeAttributes", (node) => {
    // set all elments owning target to target="_blank"
    if ("target" in node) {
        node.setAttribute("target", "_blank");
        node.setAttribute("rel", "noopener noreferrer");
    }
});

// https://vuejs.org/guide/reusability/custom-directives#function-shorthand
// It's common for a custom directive to have the same behavior for mounted and updated,
// with no need for the other hooks. In such cases we can define the directive as a function:
const SanitizeHtml = (el, binding) => {
    el.innerHTML = DOMPurify.sanitize(binding.value);
};

export default SanitizeHtml;
