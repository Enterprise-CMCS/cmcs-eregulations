# ERegs static files

# Adding linting and code formatting to static files

## Why linting and code formatting?

Linting helps find errors earlier.

Adopting a common style guide stops on-going debates about code style.

Linting and code formatting can be added to projects in many ways:

* Live feedback in text editor that validates code as it is written and provides immediate feedback
* CLI integration that can validate and format code via commands executed from the command line
* Format-on-save functionality that validates and formats code automatically when saved
* Format-on-commit functionality that validates and formats code automatically when committed to source control using a git hook
* Format-on-push functionality built into a CI/CD pipeline that validates and formats code automatically when pushing to source control

** This story will focus on text editor integration and CLI command execution.** 

## Why ESLint?

ESLint helps find and fix problems in JavaScript code.  It exposes bugs and style errors, as well as offering opinions about syntax.

[Django recommends ESLint when working with JavaScript files](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/javascript/), and also recommends installing an ESLint plugin into your text editor.

When setting up ESLint, you are asked to choose a default style guide.  **I've chosen the Airbnb style guide** because it's a very popular, [with 117k stars on github](https://github.com/airbnb/javascript). It's been around quite a while and it's the one I've been personally using for a long time.  Here's a comparison between [Airbnb, Google, and Standard](https://betterprogramming.pub/comparing-the-top-three-style-guides-and-setting-them-up-with-eslint-98ea0d2fc5b7) style guides.

Additionally, we've added the official ESLint plugin for Vue.js: [eslint-plugin-vue](https://eslint.vuejs.org/user-guide/#installation).  This will specifically [expose syntax errors, the wrong uses of Vue.js Directives, and violations of the Vue.js Style Guide](https://eslint.vuejs.org/#introduction).

And finally we've added Prettier, an opinionated code formatter.  This is another very popular library - [41.3k stars on github](https://github.com/prettier/prettier).  It complements ESLint, the Airbnb style guide, and the Vue.js plugin.

## Getting Started

[ESLint official Getting Started page](https://eslint.org/docs/user-guide/getting-started)

ESLint has been added to the package.json in `/regulations/static/`, including vue, airbnb, and prettier plugins.

`.eslintrc.json` has been created in `/regulations/static/`.  It is mainly boilerplate but adds the Airbnb style guide, the Vue.js plugin, and Prettier.

`.prettierrc.json` has been created for any overrides that we want to add.  Right now, it overrides `tabWidth` to be `4` spaces.

`.prettierignore` has been created because it was recommended by the Prettier docs.  It includes an incomplete list of file types and directories to ignore when running Prettier from the command line.

## Integrating with Text Editors (recommended)

The best way to start using ESLint is to integrate it into your text editor so you get immediate feedback while writing code.  You can manually fix these alerts yourself, or use CodeActions to automatically fix all fixable problems.

Typical workflow for using ESLint and Prettier in your text editor:

1. Write code
2. See real-time validation alerts
3. Manually change code to satisfy linter and make validation alerts disappear OR
4. Execute ESLint and Prettier code actions/keyboard shortcuts to automatically fix and format entire file

[ESLint official Integrations page](https://eslint.org/docs/user-guide/integrations)

**Note:** ESLint 8 had some breaking changing that editor plugins are only now resolving.  See notes below about plugin versions needed.

[Prettier official Editor Integration page](https://prettier.io/docs/en/editors.html)

### VSCode

[ESLint plugin for VSCode](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)
Make sure you install v2.2.x.  If there are issues installing this version, you may need to install a pre-release version from VSIX, as outlined in the comment:
[https://github.com/microsoft/vscode-eslint/issues/972#issuecomment-903573031](Why 2.2.0 needs to be installed)
[https://github.com/microsoft/vscode-eslint/releases/tag/release%2F2.2.20-Insider](VSCode ESLint releases)

[Prettier plugin for VSCode](https://prettier.io/docs/en/editors.html#visual-studio-code)

### Neovim via nvim.coc

[coc-eslint](https://github.com/neoclide/coc-eslint)

However, for the same reason a pre-release build must be used for VSCode above, a custom coc eslint plugin must also be installed for now: [coc-eslint8])https://github.com/neoclide/coc-eslint/pull/118#issuecomment-973640987)

[coc-prettier](https://prettier.io/docs/en/vim.html#coc-prettierhttpsgithubcomneoclidecoc-prettier)

### VIM via ALE

**Untested**
[https://miikanissi.com/blog/configure-eslint-prettier-ale-vim.html](Configuring ESLint and Prettier for Vim with ALE)

[Prettier plugin for use with ALE](https://prettier.io/docs/en/vim.html#alehttpsgithubcomdense-analysisale)

### JetBrains IDEs

**Untested**
[Webstorm](https://www.jetbrains.com/help/webstorm/eslint.html)
[Pycharm](https://www.jetbrains.com/help/pycharm/eslint.html)

## Using from the command line

[Official ESLint Command Line Interface page](https://eslint.org/docs/user-guide/command-line-interface)

To run ESLint from the command line, you may need to install eslint globally on your machine:

`npm i -g eslint`

There are many options from which to choose.

To use as a diagnostic tool to see problems without fixing them, use `--fix-dry-run`:

`eslint --fix-dry-run ./regulations/js/main.js`
