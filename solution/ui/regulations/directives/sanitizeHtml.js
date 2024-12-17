import DOMPurify from "dompurify";

const SanitizeHtml = (el, binding) => {
    el.innerHTML = DOMPurify.sanitize(binding.value);
};

export default SanitizeHtml;
