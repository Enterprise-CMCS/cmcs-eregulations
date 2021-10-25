//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//

var script$1 = {
    name: "action-button",

    props: {
        actionType: {
            type: String,
            required: true,
        },
        selectedAction: {
            type: String,
            required: true,
        },
        status: {
            type: String,
            required: true,
        },
    },

    computed: {
        selected() {
            return (
                this.selectedAction === this.actionType &&
                this.status !== "idle"
            );
        },
        labelState() {
            return this.selected && this.status === "success"
                ? "copied"
                : "copy";
        },
        label() {
            return `${this.labelState} ${this.actionType}`;
        },
        buttonClasses() {
            return {
                "selected-btn": this.selected && this.status === "success",
                "default-btn": !this.selected,
            };
        },
    },

    methods: {
        handleClick() {
            this.$emit("action-btn-click", {
                actionType: this.actionType,
            });
        },
    },

    filters: {},
};

function normalizeComponent(template, style, script, scopeId, isFunctionalTemplate, moduleIdentifier /* server only */, shadowMode, createInjector, createInjectorSSR, createInjectorShadow) {
    if (typeof shadowMode !== 'boolean') {
        createInjectorSSR = createInjector;
        createInjector = shadowMode;
        shadowMode = false;
    }
    // Vue.extend constructor export interop.
    const options = typeof script === 'function' ? script.options : script;
    // render functions
    if (template && template.render) {
        options.render = template.render;
        options.staticRenderFns = template.staticRenderFns;
        options._compiled = true;
        // functional template
        if (isFunctionalTemplate) {
            options.functional = true;
        }
    }
    // scopedId
    if (scopeId) {
        options._scopeId = scopeId;
    }
    let hook;
    if (moduleIdentifier) {
        // server build
        hook = function (context) {
            // 2.3 injection
            context =
                context || // cached call
                    (this.$vnode && this.$vnode.ssrContext) || // stateful
                    (this.parent && this.parent.$vnode && this.parent.$vnode.ssrContext); // functional
            // 2.2 with runInNewContext: true
            if (!context && typeof __VUE_SSR_CONTEXT__ !== 'undefined') {
                context = __VUE_SSR_CONTEXT__;
            }
            // inject component styles
            if (style) {
                style.call(this, createInjectorSSR(context));
            }
            // register component module identifier for async chunk inference
            if (context && context._registeredComponents) {
                context._registeredComponents.add(moduleIdentifier);
            }
        };
        // used by ssr in case component is cached and beforeCreate
        // never gets called
        options._ssrRegister = hook;
    }
    else if (style) {
        hook = shadowMode
            ? function (context) {
                style.call(this, createInjectorShadow(context, this.$root.$options.shadowRoot));
            }
            : function (context) {
                style.call(this, createInjector(context));
            };
    }
    if (hook) {
        if (options.functional) {
            // register for functional component in vue file
            const originalRender = options.render;
            options.render = function renderWithStyleInjection(h, context) {
                hook.call(context);
                return originalRender(h, context);
            };
        }
        else {
            // inject component registration as beforeCreate hook
            const existing = options.beforeCreate;
            options.beforeCreate = existing ? [].concat(existing, hook) : [hook];
        }
    }
    return script;
}

/* script */
const __vue_script__$1 = script$1;

/* template */
var __vue_render__$1 = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c(
    "button",
    {
      staticClass: "action-btn",
      class: _vm.buttonClasses,
      attrs: { disabled: _vm.selected && this.status === "success" },
      on: { click: _vm.handleClick }
    },
    [
      _vm.selected && this.status === "success"
        ? _c(
            "svg",
            { attrs: { width: "17", height: "17", viewBox: "0 0 17 17" } },
            [
              _c("svg", { attrs: { width: "17", height: "17" } }, [
                _c("path", {
                  attrs: {
                    "fill-rule": "evenodd",
                    "clip-rule": "evenodd",
                    d:
                      "M8.50007 16C4.36452 16 1 12.6355 1 8.50007C1 4.36452 4.36452 1 8.50007 1C12.6355 1 15.9999 4.36452 15.9999 8.50007C15.9999 12.6355 12.6355 16 8.50007 16ZM8.50007 2.02937C4.93206 2.02937 2.02922 4.93221 2.02922 8.50007C2.02922 12.0681 4.93206 14.9708 8.50007 14.9708C12.0679 14.9708 14.9706 12.0681 14.9706 8.50007C14.9706 4.93221 12.0679 2.02937 8.50007 2.02937Z",
                    fill: "#2A7A3B",
                    stroke: "#2A7A3B",
                    "stroke-width": "0.25"
                  }
                })
              ]),
              _vm._v(" "),
              _c(
                "svg",
                { attrs: { width: "17", height: "17", x: "4", y: "5" } },
                [
                  _c("path", {
                    attrs: {
                      "fill-rule": "evenodd",
                      "clip-rule": "evenodd",
                      d:
                        "M3.48221 5.98237C3.34562 5.98237 3.21476 5.92812 3.11831 5.83166L1.2191 3.93246C1.01811 3.73161 1.01811 3.40565 1.2191 3.2048C1.4201 3.00366 1.74577 3.00366 1.94676 3.2048L3.48221 4.73996L7.05287 1.1693C7.25357 0.968307 7.57954 0.968307 7.78053 1.1693C7.98152 1.37014 7.98152 1.69611 7.78053 1.89696L3.84597 5.83166C3.74951 5.92812 3.61866 5.98237 3.48221 5.98237Z",
                      fill: "#2A7A3B",
                      stroke: "#2A7A3B",
                      "stroke-width": "0.25"
                    }
                  })
                ]
              )
            ]
          )
        : _vm._e(),
      _vm._v("\n    " + _vm._s(_vm.label) + "\n")
    ]
  )
};
var __vue_staticRenderFns__$1 = [];
__vue_render__$1._withStripped = true;

  /* style */
  const __vue_inject_styles__$1 = undefined;
  /* scoped */
  const __vue_scope_id__$1 = undefined;
  /* module identifier */
  const __vue_module_identifier__$1 = undefined;
  /* functional template */
  const __vue_is_functional_template__$1 = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__$1 = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__$1, staticRenderFns: __vue_staticRenderFns__$1 },
    __vue_inject_styles__$1,
    __vue_script__$1,
    __vue_scope_id__$1,
    __vue_is_functional_template__$1,
    __vue_module_identifier__$1,
    false,
    undefined,
    undefined,
    undefined
  );

//

const getAnchorY = (el, elType) => {
    if (!el) return 0;

    return elType === "labeled-icon"
        ? el.offsetWidth / 2
        : el.offsetWidth * 0.7;
};

const getAnchorX = (el, elType) => {
    if (!el) return 0;

    return parseInt(window.getComputedStyle(el).fontSize, 10) + 20;
};

const appendPxSuffix = (int) => `${int}px`;

const leftWarning = (el) => el.getBoundingClientRect().left < 130;

var script = {
    name: "copy-btn",

    components: {
        ActionBtn: __vue_component__$1,
    },

    props: {
        btn_type: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            required: true,
        },
        hash: {
            type: String,
            required: true,
        },
        formatted_citation: {
            type: String,
            required: true,
        },
    },

    data() {
        return {
            entered: false,
            clicked: false,
            leftSafe: true,
            anchorY: 0,
            anchorX: 0,
            label: "Copy Link or Citation",
            selectedAction: null,
            copyStatus: "idle",
        };
    },

    computed: {
        ariaLabel() {
            return this.btn_type === "icon"
                ? `${this.label} for ${this.title}`
                : false;
        },
        buttonClasses() {
            return {
                "copy-btn-labeled": this.btn_type === "labeled-icon",
            };
        },
        tooltipClasses() {
            return {
                "tooltip-caret": this.leftSafe,
                "tooltip-caret-left": !this.leftSafe,
            };
        },
        tooltipStyles() {
            return {
                left: this.anchorY,
                bottom: this.anchorX,
                transform: `translate(-${this.leftSafe ? 50 : 20}%, 0)`,
            };
        },
    },

    watch: {
        copyStatus: async function (newStatus, oldStatus) {
            if (
                newStatus === "pending" &&
                (oldStatus === "idle" || oldStatus === "success")
            ) {
                try {
                    // async write to clipboard
                    await navigator.clipboard.writeText(this.getCopyText());
                    this.copyStatus = "success";
                } catch (err) {
                    console.log("Error copying to clipboard", err);
                    this.copyStatus = "idle";
                }
            }
        },
    },

    // https://www.vuesnippets.com/posts/click-away/
    // https://dev.to/jamus/clicking-outside-the-box-making-your-vue-app-aware-of-events-outside-its-world-53nh
    directives: {
        clickaway: {
            bind(el, { value }) {
                if (typeof value !== "function") {
                    console.warn(`Expect a function, got ${value}`);
                    return;
                }

                const clickawayHandler = (e) => {
                    const elementsOfInterest = Array.from(
                        el.parentElement.children
                    );
                    const clickedInside = elementsOfInterest.filter((el) =>
                        el.contains(e.target)
                    );
                    return clickedInside.length || value();
                };

                el.__clickawayEventHandler__ = clickawayHandler;

                document.addEventListener("click", clickawayHandler);
            },
            unbind(el) {
                document.removeEventListener(
                    "click",
                    el.__clickawayEventHandler__
                );
            },
        },
    },

    methods: {
        handleEnter(e) {
            this.entered = !this.entered && !this.clicked;
            this.leftSafe = !leftWarning(e.currentTarget);
            this.anchorY = appendPxSuffix(
                getAnchorY(e.currentTarget, this.btn_type)
            );
            this.anchorX = appendPxSuffix(getAnchorX(this.$el, this.btn_type));
        },
        handleExit() {
            if (!this.clicked) {
                this.entered = false;
                this.anchorY = undefined;
                this.leftSafe = true;
            }
        },
        handleClick(e) {
            if (!this.clicked) {
                this.entered = false;
                this.clicked = true;
                if (leftWarning(e.currentTarget)) {
                    this.leftSafe = false;
                }
                this.anchorY = appendPxSuffix(
                    getAnchorY(e.currentTarget, this.btn_type)
                );
                this.anchorX = appendPxSuffix(
                    getAnchorX(this.$el, this.btn_type)
                );
            }
        },
        handleCloseClick() {
            if (this.clicked) {
                this.clicked = false;
                this.entered = false;
                this.anchorY = undefined;
                this.leftSafe = true;
                this.selectedAction = null;
            }
        },
        handleActionClick(payload) {
            this.selectedAction = payload.actionType;
            this.copyStatus = "pending";
        },
        getCopyText() {
            return this.selectedAction === "citation"
                ? this.formatted_citation
                : `${new URL(window.location.href.split("#")[0]).toString()}#${
                      this.hash
                  }`;
        },
    },
};

/* script */
const __vue_script__ = script;

/* template */
var __vue_render__ = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c("div", { staticClass: "copy-btn-container" }, [
    _c(
      "button",
      {
        staticClass: "copy-btn text-btn",
        class: _vm.buttonClasses,
        attrs: { "aria-label": _vm.ariaLabel },
        on: {
          focus: _vm.handleEnter,
          focusout: _vm.handleExit,
          mouseenter: _vm.handleEnter,
          mouseleave: _vm.handleExit,
          click: _vm.handleClick
        }
      },
      [
        _c("i", { staticClass: "fa fa-link" }),
        _vm._v(" "),
        _vm.btn_type === "labeled-icon"
          ? _c("span", [_vm._v(_vm._s(_vm.label))])
          : _vm._e()
      ]
    ),
    _vm._v(" "),
    _c(
      "div",
      {
        directives: [
          {
            name: "show",
            rawName: "v-show",
            value: _vm.entered && _vm.btn_type === "icon",
            expression: "entered && btn_type === 'icon'"
          }
        ],
        staticClass: "copy-tooltip hovered",
        class: _vm.tooltipClasses,
        style: _vm.tooltipStyles
      },
      [_c("p", { staticClass: "hover-msg" }, [_vm._v(_vm._s(_vm.label))])]
    ),
    _vm._v(" "),
    _vm.clicked
      ? _c(
          "div",
          {
            directives: [
              {
                name: "clickaway",
                rawName: "v-clickaway",
                value: _vm.handleCloseClick,
                expression: "handleCloseClick"
              }
            ],
            staticClass: "copy-tooltip clicked",
            class: _vm.tooltipClasses,
            style: _vm.tooltipStyles
          },
          [
            _c(
              "button",
              {
                staticClass: "close-btn text-btn",
                attrs: { "aria-label": "close copy link or citation dialog" },
                on: { click: _vm.handleCloseClick }
              },
              [
                _c(
                  "svg",
                  {
                    attrs: {
                      width: "11",
                      height: "11",
                      viewBox: "0 0 11 11",
                      fill: "none",
                      xmlns: "http://www.w3.org/2000/svg"
                    }
                  },
                  [
                    _c("path", {
                      attrs: {
                        "fill-rule": "evenodd",
                        "clip-rule": "evenodd",
                        d:
                          "M1.47149 1.08383L5.49969 5.11209L9.52851 1.08383C9.63637 0.975965 9.81124 0.975965 9.91911 1.08383C10.027 1.19169 10.027 1.36656 9.91911 1.47442L5.89023 5.50262L9.91911 9.53144C10.027 9.6393 10.027 9.81417 9.91911 9.92204C9.81124 10.0299 9.63637 10.0299 9.52851 9.92204L5.49969 5.89316L1.47149 9.92204C1.36363 10.0299 1.18876 10.0299 1.0809 9.92204C0.973035 9.81417 0.973035 9.6393 1.0809 9.53144L5.10916 5.50262L1.0809 1.47442C0.973035 1.36656 0.973035 1.19169 1.0809 1.08383C1.18876 0.975965 1.36363 0.975965 1.47149 1.08383Z"
                      }
                    })
                  ]
                )
              ]
            ),
            _vm._v(" "),
            _c("p", { staticClass: "citation-title" }, [
              _vm._v(_vm._s(this.formatted_citation))
            ]),
            _vm._v(" "),
            _c(
              "div",
              { staticClass: "action-btns" },
              [
                _c("ActionBtn", {
                  attrs: {
                    selectedAction: _vm.selectedAction,
                    status: _vm.copyStatus,
                    actionType: "link"
                  },
                  on: { "action-btn-click": _vm.handleActionClick }
                }),
                _vm._v(" "),
                _c("ActionBtn", {
                  attrs: {
                    selectedAction: _vm.selectedAction,
                    status: _vm.copyStatus,
                    actionType: "citation"
                  },
                  on: { "action-btn-click": _vm.handleActionClick }
                })
              ],
              1
            )
          ]
        )
      : _vm._e()
  ])
};
var __vue_staticRenderFns__ = [];
__vue_render__._withStripped = true;

  /* style */
  const __vue_inject_styles__ = undefined;
  /* scoped */
  const __vue_scope_id__ = undefined;
  /* module identifier */
  const __vue_module_identifier__ = undefined;
  /* functional template */
  const __vue_is_functional_template__ = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__ = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__, staticRenderFns: __vue_staticRenderFns__ },
    __vue_inject_styles__,
    __vue_script__,
    __vue_scope_id__,
    __vue_is_functional_template__,
    __vue_module_identifier__,
    false,
    undefined,
    undefined,
    undefined
  );

export default __vue_component__;
//# sourceMappingURL=CopyBtn.js.map
