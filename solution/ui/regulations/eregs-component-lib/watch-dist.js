// https://stackoverflow.com/questions/38032047/how-to-execute-npm-run-command-programmatically
import chokidar from "chokidar";
import shell from "shelljs";

// Initialize watchers.
const distWatcher = chokidar.watch("./dist");
const mainWatcher = chokidar.watch("./src/main.js");

// Something to use when events are received.
const log = console.log.bind(console);

distWatcher
    .on("add", (path) => {
        log(`File ${path} has been added`);
        shell.exec("npm run build:main");
    })
    .on("change", (path) => {
        log(`File ${path} has been changed`);
    })
    .on("unlink", (path) => {
        log(`File ${path} has been unlinked`);
    });

mainWatcher
    .on("add", (path) => {
        log(`File ${path} has been added`);
        shell.exec("npm run build:main");
    })
    .on("change", (path) => {
        log(`File ${path} has been changed`);
        shell.exec("npm run build:main");
    })
    .on("unlink", (path) => {
        log(`File ${path} has been unlinked`);
    });
