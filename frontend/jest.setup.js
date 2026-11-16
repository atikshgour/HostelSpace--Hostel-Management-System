/* Owner: Anvi Srinivas | US-17,US-21 | Dev sprint 1; 4–6 | SRS sprint 1; 6 | Reviewer: Arin Singh (pending) */
import "@testing-library/jest-dom";

if (typeof HTMLDialogElement !== "undefined" && !HTMLDialogElement.prototype.showModal)
  HTMLDialogElement.prototype.showModal = function () {
    this.open = true;
  };
if (typeof HTMLDialogElement !== "undefined" && !HTMLDialogElement.prototype.close)
  HTMLDialogElement.prototype.close = function () {
    this.open = false;
  };
