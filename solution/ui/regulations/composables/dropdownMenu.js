// https://vuejs.org/guide/reusability/composables
import { ref } from "vue";

export default function useDropdownMenu() {
    const menuExpanded = ref(false);

    const toggleClick = () => {
        menuExpanded.value = !menuExpanded.value;
    };

    const closeClick = () => {
        menuExpanded.value = false;
    };

    return {
        menuExpanded,
        toggleClick,
        closeClick,
    };
}
