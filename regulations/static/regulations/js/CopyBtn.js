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
    },

    data: function () {
        return {
            entered: false,
            clicked: false,
            leftAnchorPos: undefined,
            label: "Copy Link or Citation",
        };
    },

    computed: {
        classObject() {
            return {
                "copy-btn-labeled": this.btn_type === "labeled-icon",
            };
        },
        enteredStyles() {
            return {
                left: this.leftAnchorPos,
                transform: "translate(-50%, 0)",
            };
        },
    },

    methods: {
        handleEnter(e) {
            if (!this.entered && !this.clicked) this.entered = true;
            this.leftAnchorPos = appendPxSuffix(
                getAnchorPos(e.currentTarget, this.btn_type)
            );
        },
        handleExit(e) {
            if (!this.clicked) {
                this.entered = false;
                this.leftAnchorPos = undefined;
            }
        },
        handleClick(e) {
            this.entered = false;
            this.clicked = true;
            this.leftAnchorPos = appendPxSuffix(
                getAnchorPos(e.currentTarget, this.btn_type)
            );
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
  return _c(
    "button",
    {
      staticClass: "copy-btn",
      class: _vm.classObject,
      attrs: {
        title: _vm.title,
        "aria-label": _vm.btn_type === "icon" ? _vm.label : false
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
        : _vm._e(),
      _vm._v(" "),
      _c(
        "div",
        {
          directives: [
            {
              name: "show",
              rawName: "v-show",
              value: _vm.entered,
              expression: "entered"
            }
          ],
          staticClass: "copy-tooltip hovered",
          style: _vm.enteredStyles
        },
        [_c("p", { staticClass: "hover-msg" }, [_vm._v(_vm._s(_vm.label))])]
      )
    ]
  )
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
