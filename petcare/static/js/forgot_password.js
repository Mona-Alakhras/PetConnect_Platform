/**
 * Forgot password — submits the reset request without leaving the page.
 * Falls back to a normal form POST if JavaScript is unavailable.
 */
(function () {
  "use strict";
 
  const form = document.getElementById("forgotPasswordForm");
  const output = document.getElementById("forgotMessage");
 
  if (!form || !output) {
    return;
  }
 
  form.addEventListener("submit", function (event) {
    event.preventDefault();
 
    const submitButton = form.querySelector("button[type='submit']");
    const csrfInput = form.querySelector("[name=csrfmiddlewaretoken]");
 
    if (submitButton) {
      submitButton.disabled = true;
    }
    output.className = "auth-inline-message";
    output.textContent = "Sending…";
 
    fetch(form.dataset.asyncAction || form.action, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfInput ? csrfInput.value : "",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(new FormData(form)),
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        output.className =
          "auth-inline-message auth-inline-message--" + (data.success ? "success" : "error");
        output.textContent = data.message;
 
        if (data.success) {
          form.reset();
        }
      })
      .catch(function () {
        output.className = "auth-inline-message auth-inline-message--error";
        output.textContent = "Network error — please try again.";
      })
      .finally(function () {
        if (submitButton) {
          submitButton.disabled = false;
        }
      });
  });
})();