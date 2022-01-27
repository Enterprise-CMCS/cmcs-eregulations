---
inject: true
to: ui/regulations/js/main.js
before: "#### HYGEN IMPORT INSERTION POINT DO NOT REMOVE ####"
---
import <%= name %>Component from "../dist/<%= name %>Component";