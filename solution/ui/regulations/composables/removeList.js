export default function useRemoveList({ route, removeList = [] }) {
    const routeClone = { ...route };

    removeList.forEach((item) => {
        if (routeClone[item]) {
            delete routeClone[item];
        }
    });

    return routeClone;
}
