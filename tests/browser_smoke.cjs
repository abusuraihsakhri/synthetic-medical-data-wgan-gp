// Execute the browser-only demo against a minimal DOM without external dependencies.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const html = fs.readFileSync("web/index.html", "utf8");
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, "Expected an inline browser script");

function element(initial = {}) {
  return Object.assign({
    value: "",
    checked: false,
    disabled: false,
    textContent: "",
    handlers: {},
    addEventListener(type, handler) { this.handlers[type] = handler; },
    reportValidity() { return true; },
  }, initial);
}
const controls = {
  auditForm: element(),
  outputConsole: element(),
  resultStatus: element(),
  downloadButton: element(),
  resetButton: element(),
  "m-tasks": element(),
  "m-alerts": element(),
  "m-critical": element(),
  task_id: element({value: "TEST-001"}),
  target_id: element({value: "SAMPLE-A"}),
  primary_metric: element({value: "10"}),
  secondary_metric: element({value: "2"}),
  status_descriptor: element({value: "NOMINAL"}),
  is_critical: element({checked: false}),
};
let sentRequests = 0;
let downloaded = 0;
const sandbox = {
  document: {
    getElementById(id) { assert.ok(controls[id], id); return controls[id]; },
    createElement(tag) {
      assert.equal(tag, "a");
      return {click() { downloaded += 1; }, set href(v) {}, set download(v) {}};
    },
  },
  Blob,
  URL: {createObjectURL() { return "blob:local"; }, revokeObjectURL() {}},
  fetch() { sentRequests += 1; throw new Error("Unexpected network request"); },
};
vm.runInNewContext(match[1], sandbox, {filename:"browser.js"});
const submit = () => controls.auditForm.handlers.submit({preventDefault() {}});
const dossier = () => JSON.parse(controls.outputConsole.textContent);

submit();
assert.equal(dossier().overall_urgency, "ROUTINE");
assert.equal(dossier().total_alerts, 0);
assert.equal(controls["m-tasks"].textContent, "1");

controls.primary_metric.value = "27";
controls.secondary_metric.value = "13";
controls.status_descriptor.value = "ANOMALY";
controls.is_critical.checked = false;
submit();
assert.equal(dossier().overall_urgency, "ELEVATED_RISK");
assert.equal(dossier().total_alerts, 3);

controls.is_critical.checked = true;
submit();
assert.equal(dossier().overall_urgency, "CRITICAL_STAT_PANIC");
assert.equal(dossier().critical_alerts_count, 1);
assert.equal(controls["m-critical"].textContent, "1");
controls.downloadButton.handlers.click();
assert.equal(downloaded, 1);
assert.equal(sentRequests, 0);

controls.auditForm.handlers.reset();
assert.equal(controls.downloadButton.disabled, true);
console.log("Browser local audit and JSON export: OK");
