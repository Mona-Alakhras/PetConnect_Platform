/**
 * PetConnect — global behaviour shared by every page.
 * Loaded with `defer`, so the DOM is ready by the time this runs.
 */
(function () {
  "use strict";
 
  /* ---------------------------------------------------------------
   * Navbar: add a "scrolled" class once the page moves past the hero
   * ------------------------------------------------------------- */
  const navbar = document.querySelector(".navbar");
 
  if (navbar) {
    let ticking = false;
 
    const syncNavbar = function () {
      navbar.classList.toggle("scrolled", window.scrollY > 50);
      ticking = false;
    };
 
    window.addEventListener(
      "scroll",
      function () {
        if (!ticking) {
          window.requestAnimationFrame(syncNavbar);
          ticking = true;
        }
      },
      { passive: true }
    );
 
    syncNavbar();
  }
 
  /* ---------------------------------------------------------------
   * Mobile menu: close it after following a link or pressing Escape
   * ------------------------------------------------------------- */
  const navToggle = document.getElementById("nav-toggle");
 
  if (navToggle) {
    document.querySelectorAll(".navbar__menu a").forEach(function (link) {
      link.addEventListener("click", function () {
        navToggle.checked = false;
      });
    });
 
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        navToggle.checked = false;
      }
    });
  }
 
  /* ---------------------------------------------------------------
   * Flash messages: dismissible, and self-dismissing after 6 seconds
   * ------------------------------------------------------------- */
  const dismiss = function (flash) {
    flash.classList.add("flash--leaving");
    flash.addEventListener("transitionend", function () {
      flash.remove();
    });
  };
 
  document.querySelectorAll(".flash").forEach(function (flash) {
    const closeBtn = flash.querySelector(".flash__close");
 
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        dismiss(flash);
      });
    }
 
    window.setTimeout(function () {
      if (flash.isConnected) {
        dismiss(flash);
      }
    }, 6000);
  });
 
  /* ---------------------------------------------------------------
   * Confirmation prompts for destructive actions
   * Any form carrying `data-confirm="…"` asks before submitting.
   * ------------------------------------------------------------- */
  document.addEventListener("submit", function (event) {
    const form = event.target;
    const message = form.dataset ? form.dataset.confirm : null;
 
    if (message && !window.confirm(message)) {
      event.preventDefault();
    }
  });
})();