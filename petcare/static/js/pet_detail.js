/**
 * Pet detail page — gallery thumbnails and the adoption request dialog.
 */
(function () {
  "use strict";
 
  /* ---------------------------------------------------------------
   * Gallery: clicking a thumbnail swaps the main photo
   * ------------------------------------------------------------- */
  const mainImage = document.getElementById("galleryMain");
  const thumbnails = document.querySelectorAll(".pet-gallery__thumb");
 
  thumbnails.forEach(function (thumb) {
    thumb.addEventListener("click", function () {
      if (!mainImage) {
        return;
      }
 
      mainImage.src = thumb.dataset.full;
      thumbnails.forEach(function (other) {
        other.classList.toggle("is-active", other === thumb);
      });
    });
  });
 
  /* ---------------------------------------------------------------
   * Adoption dialog
   * ------------------------------------------------------------- */
  const modal = document.getElementById("adoptModal");
 
  if (!modal) {
    return;
  }
 
  let lastFocused = null;
 
  const openModal = function (trigger) {
    lastFocused = trigger || document.activeElement;
    modal.hidden = false;
    modal.style.display = "flex";
    document.body.style.overflow = "hidden";
 
    const firstField = modal.querySelector("textarea, input:not([disabled]), button");
    if (firstField) {
      firstField.focus();
    }
  };
 
  const closeModal = function () {
    modal.hidden = true;
    modal.style.display = "none";
    document.body.style.overflow = "";
 
    if (lastFocused) {
      lastFocused.focus();
    }
  };
 
  document.querySelectorAll('[data-open-modal="adoptModal"]').forEach(function (trigger) {
    trigger.addEventListener("click", function () {
      openModal(trigger);
    });
  });
 
  modal.querySelectorAll("[data-close-modal]").forEach(function (trigger) {
    trigger.addEventListener("click", closeModal);
  });
 
  // Clicking the backdrop (but not the dialog itself) closes it.
  modal.addEventListener("click", function (event) {
    if (event.target === modal) {
      closeModal();
    }
  });
 
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !modal.hidden) {
      closeModal();
    }
  });
})();