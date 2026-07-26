/**
 * My Requests — client-side status filter.
 * The full list is rendered server-side, so filtering here is safe.
 */
(function () {
  "use strict";
 
  const buttons = document.querySelectorAll(".filter-btn");
  const cards = document.querySelectorAll(".request-card");
  const emptyNotice = document.getElementById("noMatchingRequests");
 
  if (!buttons.length) {
    return;
  }
 
  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      const status = button.dataset.filter;
      let visible = 0;
 
      buttons.forEach(function (other) {
        other.classList.toggle("active", other === button);
      });
 
      cards.forEach(function (card) {
        const matches = status === "all" || card.dataset.status === status;
        card.hidden = !matches;
        if (matches) {
          visible += 1;
        }
      });
 
      if (emptyNotice) {
        emptyNotice.hidden = visible !== 0 || cards.length === 0;
      }
    });
  });
})();