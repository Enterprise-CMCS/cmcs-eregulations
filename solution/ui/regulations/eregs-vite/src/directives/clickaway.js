// https://www.vuesnippets.com/posts/click-away/
// https://dev.to/jamus/clicking-outside-the-box-making-your-vue-app-aware-of-events-outside-its-world-53nh
const Clickaway = {
    bind(el, { value }) {
        if (typeof value !== "function") {
            console.warn(`Expect a function, got ${value}`);
            return;
        }

        const clickawayHandler = (e) => {
            const elementsOfInterest = Array.from(el.parentElement.children);
            const clickedInside = elementsOfInterest.filter((element) =>
                element.contains(e.target)
            );
            return clickedInside.length || value();
        };

        el.__clickawayEventHandler__ = clickawayHandler;

        document.addEventListener("click", clickawayHandler);
    },
    unbind(el) {
        document.removeEventListener("click", el.__clickawayEventHandler__);
    },
};

export default Clickaway;
