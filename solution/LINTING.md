# ERegs static files

## Adding linting and code formatting to static files

### Why linting and code formatting?

Linting helps find errors earlier.

Adopting a common style guide stops on-going debates about code style.

Linting and code formatting can be added to projects in many ways:

* Live feedback in text editor that validates code as it is written and provides immediate feedback
* CLI integration that can validate and format code via commands executed from the command line
* CI/CD integration that can validate code as part of the build process

### Why ESLint?

ESLint helps find and fix problems in JavaScript and TypeScript code.  It exposes bugs and style errors, as well as offering opinions about syntax.

[Django recommends ESLint when working with JavaScript files](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/javascript/), and also recommends installing an ESLint plugin into your text editor.

We've added the official ESLint plugin for Vue.js: [eslint-plugin-vue](https://eslint.vuejs.org/user-guide/#installation).  This will specifically [expose syntax errors, the wrong uses of Vue.js Directives, and violations of the Vue.js Style Guide](https://eslint.vuejs.org/#introduction).

### Getting Started

ESLint will run as a GitHub Action on every pull request.  If you want to run ESLint locally, you can do so by running the following commands from `./solution`:

```
// lint the entire project
make eslint
```

This will return a list of errors and warnings that need to be fixed.

### Integrating with Text Editors (recommended)

The best way to start using ESLint is to integrate it into your text editor so you get immediate feedback while writing code.  You can manually fix these alerts yourself, or use CodeActions to automatically fix all fixable problems.

Typical workflow for using ESLint in your text editor:

1. Write code
2. See real-time validation alerts
3. Manually change code to satisfy linter and make validation alerts disappear OR
4. Execute ESLint code actions/keyboard shortcuts to automatically fix and format entire file

[ESLint official Integrations page](https://eslint.org/docs/user-guide/integrations)

#### VSCode

[ESLint plugin for VSCode](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)

#### Neovim with `mason.nvim` and `lspconfig`

[mason-lspconfig.nvim](https://github.com/williamboman/mason-lspconfig.nvim)

#### Neovim via `nvim.coc`

[coc-eslint](https://github.com/neoclide/coc-eslint)

#### VIM via ALE - Untested

[Configuring ESLint and Prettier for Vim with ALE](https://miikanissi.com/blog/configure-eslint-prettier-ale-vim.html)

[Prettier plugin for use with ALE](https://prettier.io/docs/en/vim.html#alehttpsgithubcomdense-analysisale)

#### JetBrains IDEs - Untested

[Webstorm](https://www.jetbrains.com/help/webstorm/eslint.html)

[Pycharm](https://www.jetbrains.com/help/pycharm/eslint.html)
