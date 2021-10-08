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

const getAnchorPos = (el, elType) => {
    if (!el) return 0;

    return elType === "labeled-icon"
        ? el.offsetWidth / 2
        : el.offsetWidth * 0.7;
};

const appendPxSuffix = (int) => `${int}px`;

const leftWarning = (el) => el.getBoundingClientRect().left < 130;

var script = {
    name: "copy-btn",

    props: {
        btn_type: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            required: true,
        },
        formatted_citation: {
            type: String,
            required: true,
        },
    },

    data: function () {
        return {
            entered: false,
            clicked: false,
            leftSafe: true,
            anchorPos: undefined,
            label: "Copy Link or Citation",
        };
    },

    computed: {
        ariaLabel() {
            return `${this.label} for ${this.title}`;
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
                left: this.anchorPos,
                transform: `translate(-${this.leftSafe ? 50 : 20}%, 0)`,
            };
        },
    },

    methods: {
        handleEnter(e) {
            if (!this.entered && !this.clicked) this.entered = true;
            if (leftWarning(e.currentTarget)) {
                this.leftSafe = false;
            }
            this.anchorPos = appendPxSuffix(
                getAnchorPos(e.currentTarget, this.btn_type)
            );
        },
        handleExit() {
            if (!this.clicked) {
                this.entered = false;
                this.anchorPos = undefined;
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
                this.anchorPos = appendPxSuffix(
                    getAnchorPos(e.currentTarget, this.btn_type)
                );
            }
        },
        handleCloseClick() {
            if (this.clicked) {
                this.clicked = false;
                this.entered = false;
                this.anchorPos = undefined;
                this.leftSafe = true;
            }
        },
    },
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
        attrs: {
          "aria-label": _vm.btn_type === "icon" ? _vm.ariaLabel : false
        },
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
            _vm._m(0)
          ]
        )
      : _vm._e()
  ])
};
var __vue_staticRenderFns__ = [
  function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c("div", { staticClass: "btn-row" }, [
      _c("button", [_vm._v("One")]),
      _vm._v(" "),
      _c("button", [_vm._v("Two")])
    ])
  }
];
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
