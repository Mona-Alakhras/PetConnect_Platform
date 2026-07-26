/**
 * Owner dashboard — section tabs, photo carousels and inline request actions.
 */
(function () {
  "use strict";
 
  const sections = Array.from(document.querySelectorAll(".dashboard-section"));
  const buttons = Array.from(document.querySelectorAll(".sidebar-btn"));
  const sectionIds = sections.map(function (section) {
    return section.id;
  });
 
  /* ---------------------------------------------------------------
   * Section tabs
   * ------------------------------------------------------------- */
  function openSection(id, updateHash) {
    if (sectionIds.indexOf(id) === -1) {
      id = sectionIds[0];
    }
 
    sections.forEach(function (section) {
      section.hidden = section.id !== id;
    });
 
    buttons.forEach(function (button) {
      button.classList.toggle("active", button.dataset.section === id);
    });
 
    if (updateHash && window.history.replaceState) {
      window.history.replaceState(null, "", "#" + id);
    }
  }
 
  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      openSection(button.dataset.section, true);
    });
  });
 
  // Decide which panel to show on load: the URL hash wins, then a
  // ?page= parameter (which only ever comes from the My Pets pager).
  const hash = window.location.hash.replace("#", "");
  const hasPageParam = new URLSearchParams(window.location.search).has("page");
 
  if (sectionIds.indexOf(hash) !== -1) {
    openSection(hash, false);
  } else if (hasPageParam) {
    openSection("mypets", false);
  } else {
    openSection(sectionIds[0], false);
  }
 
  // Keep the pager inside the My Pets panel after a reload.
  document.querySelectorAll("#mypets .pagination__link").forEach(function (link) {
    if (link.hash !== "#mypets") {
      link.href = link.href.split("#")[0] + "#mypets";
    }
  });
 
  /* ---------------------------------------------------------------
   * Photo carousels
   * ------------------------------------------------------------- */
  document.querySelectorAll(".carousel-btn").forEach(function (button) {
    button.addEventListener("click", function () {
      const carousel = button.closest(".pet-card-carousel");
      const track = carousel.querySelector(".carousel-track");
      const slideCount = track.querySelectorAll(".carousel-slide").length;
      const direction = parseInt(button.dataset.slide, 10) || 1;
 
      let index = parseInt(carousel.dataset.index, 10) || 0;
      index = (index + direction + slideCount) % slideCount;
 
      carousel.dataset.index = index;
      track.style.transform = "translateX(-" + index * 100 + "%)";
    });
  });
 
  /* ---------------------------------------------------------------
   * Approve / reject without a page reload
   * ------------------------------------------------------------- */
  document.addEventListener("submit", function (event) {
    const form = event.target;
 
    if (!form.classList.contains("ajax-request-form")) {
      return;
    }
 
    event.preventDefault();
 
    const buttons = form.querySelectorAll("button");
    buttons.forEach(function (button) {
      button.disabled = true;
    });
 
    const csrfInput = form.querySelector("input[name='csrfmiddlewaretoken']");
 
    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: {
        "X-CSRFToken": csrfInput ? csrfInput.value : "",
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then(function (response) {
        return response.json().then(function (data) {
          return { ok: response.ok, data: data };
        });
      })
      .then(function (result) {
        const row = form.closest("tr");
 
        if (!result.data.success) {
          window.alert(result.data.message || "That request could not be updated.");
          if (row && result.data.status) {
            renderRow(row, result.data.status);
          } else {
            buttons.forEach(function (button) {
              button.disabled = false;
            });
          }
          return;
        }
 
        if (row) {
          renderRow(row, result.data.status);
        }
 
        // Approving a pet rejects the other pending requests for it, so the
        // rest of the table needs to catch up.
        if (result.data.pet_status === "Adopted") {
          window.location.reload();
        }
      })
      .catch(function (error) {
        console.error("Adoption request update failed:", error);
        window.alert("Network error — please try again.");
        buttons.forEach(function (button) {
          button.disabled = false;
        });
      });
  });
 
  function renderRow(row, status) {
    const statusCell = row.querySelector(".status-cell");
    const actionCell = row.querySelector(".action-cell");
    const cssClass = status.toLowerCase();
 
    if (statusCell) {
      statusCell.textContent = "";
      const badge = document.createElement("span");
      badge.className = "status " + cssClass;
      badge.textContent = status;
      statusCell.appendChild(badge);
    }
 
    if (actionCell) {
      actionCell.textContent = "—";
    }
  }
})();