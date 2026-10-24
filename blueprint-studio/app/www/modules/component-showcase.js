/** COMPONENT-SHOWCASE.JS | Isolated visual fixtures for shared frontend primitives. */
import { closeDialog, openDialog } from "./dialog-manager.js";
import { notify } from "./feedback-service.js";
import { initTooltips } from "./tooltip.js";

const body = document.body;
const dialogOverlay = document.getElementById("showcase-dialog-overlay");
const dialogTrigger = document.getElementById("showcase-dialog-trigger");

document.querySelectorAll("[data-theme-option]").forEach((button) => {
  button.addEventListener("click", () => {
    const theme = button.dataset.themeOption;
    body.dataset.showcaseTheme = theme;
    document.querySelectorAll("[data-theme-option]").forEach((option) => {
      option.setAttribute("aria-pressed", String(option === button));
    });
  });
});

document.querySelectorAll(".showcase-specimen .ui-segmented-control").forEach((control) => {
  control.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    control.querySelectorAll("button").forEach((option) => {
      option.setAttribute("aria-pressed", String(option === button));
    });
  });
});

document.querySelectorAll(".ui-tabs").forEach((tablist) => {
  tablist.addEventListener("click", (event) => {
    const tab = event.target.closest('[role="tab"]');
    if (!tab) return;
    tablist.querySelectorAll('[role="tab"]').forEach((option) => {
      option.setAttribute("aria-selected", String(option === tab));
    });
  });
});

document.getElementById("showcase-notification")?.addEventListener("click", () => {
  notify("Blueprint saved successfully", {
    type: "success",
    duration: 0,
    key: "showcase-notification",
  });
});

function closeShowcaseDialog() {
  closeDialog(dialogOverlay);
}

dialogTrigger?.addEventListener("click", () => {
  openDialog(dialogOverlay, {
    initialFocus: '[data-dialog-close]',
    returnFocus: dialogTrigger,
    onRequestClose: closeShowcaseDialog,
  });
});

dialogOverlay?.querySelectorAll("[data-dialog-close]").forEach((button) => {
  button.addEventListener("click", closeShowcaseDialog);
});

initTooltips();
