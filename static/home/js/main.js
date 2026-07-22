(function () {
  "use strict";

  /* ---------------------------------------------------------------
   * Theme switcher: light / dark / system, persisted in localStorage.
   * The blocking script in <head> already applied the theme before
   * first paint (see base.html) — this just wires up the UI and
   * keeps things in sync if the OS theme changes while "system" is
   * selected.
   * ------------------------------------------------------------- */
  var THEME_KEY = "ikco-theme";
  var root = document.documentElement;
  var mql = window.matchMedia("(prefers-color-scheme: dark)");

  function getStoredTheme() {
    try {
      return localStorage.getItem(THEME_KEY) || "system";
    } catch (e) {
      return "system";
    }
  }

  function applyTheme(theme) {
    var resolved = theme === "system" ? (mql.matches ? "dark" : "light") : theme;
    root.setAttribute("data-theme", resolved);
  }

  function setTheme(theme) {
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {
      /* ignore storage errors (private mode, etc.) */
    }
    applyTheme(theme);
    updateThemeMenuState(theme);
  }

  function updateThemeMenuState(theme) {
    document.querySelectorAll(".theme-option").forEach(function (btn) {
      var isActive = btn.getAttribute("data-theme-choice") === theme;
      btn.setAttribute("aria-checked", isActive ? "true" : "false");
    });
    var iconLight = document.getElementById("theme-icon-light");
    var iconDark = document.getElementById("theme-icon-dark");
    var resolved = theme === "system" ? (mql.matches ? "dark" : "light") : theme;
    if (iconLight && iconDark) {
      iconLight.style.display = resolved === "dark" ? "none" : "block";
      iconDark.style.display = resolved === "dark" ? "block" : "none";
    }
  }

  updateThemeMenuState(getStoredTheme());

  mql.addEventListener("change", function () {
    if (getStoredTheme() === "system") {
      applyTheme("system");
      updateThemeMenuState("system");
    }
  });

  document.querySelectorAll(".theme-option").forEach(function (btn) {
    btn.addEventListener("click", function () {
      setTheme(btn.getAttribute("data-theme-choice"));
      closeThemeSwitcher();
    });
  });

  var themeSwitcher = document.getElementById("theme-switcher");
  var themeToggle = document.getElementById("theme-switcher-toggle");

  function closeThemeSwitcher() {
    if (!themeSwitcher) return;
    themeSwitcher.classList.remove("open");
    if (themeToggle) themeToggle.setAttribute("aria-expanded", "false");
  }

  if (themeSwitcher && themeToggle) {
    themeToggle.addEventListener("click", function (event) {
      event.stopPropagation();
      var isOpen = themeSwitcher.classList.toggle("open");
      themeToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
  }

  /* Now that the theme is settled, allow transitions again. */
  requestAnimationFrame(function () {
    root.classList.remove("theme-init");
  });

  /* ---------------------------------------------------------------
   * Mobile nav drawer toggle
   * ------------------------------------------------------------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("main-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      if (!isOpen) {
        closeAllDropdowns(null);
      }
    });
  }

  /* ---------------------------------------------------------------
   * Working Groups header dropdown.
   *
   * Behaviour (required):
   *   - closed by default
   *   - opens only on click of the "کارگروه‌ها" trigger
   *   - clicking it again closes it
   *   - clicking outside closes it
   *   - Escape closes it
   *   - smooth open/close animation (handled purely in CSS via the
   *     `.open` class — see .dropdown-panel / .dropdown-caret rules)
   *   - collapsible on mobile inside the nav drawer
   * ------------------------------------------------------------- */
  var dropdownItems = document.querySelectorAll(".nav-item-dropdown");

  function closeDropdown(item) {
    item.classList.remove("open");
    var button = item.querySelector(".dropdown-toggle");
    if (button) {
      button.setAttribute("aria-expanded", "false");
    }
  }

  function closeAllDropdowns(except) {
    dropdownItems.forEach(function (item) {
      if (item !== except) {
        closeDropdown(item);
      }
    });
  }

  dropdownItems.forEach(function (item) {
    var button = item.querySelector(".dropdown-toggle");
    if (!button) {
      return;
    }

    button.addEventListener("click", function (event) {
      event.stopPropagation();
      var isOpen = item.classList.contains("open");
      closeAllDropdowns(item);
      if (isOpen) {
        closeDropdown(item);
      } else {
        item.classList.add("open");
        button.setAttribute("aria-expanded", "true");
        var firstLink = item.querySelector(".dropdown-menu a");
        if (firstLink) {
          firstLink.focus({ preventScroll: true });
        }
      }
    });
  });

  document.addEventListener("click", function (event) {
    closeAllDropdowns(null);
    if (themeSwitcher && !themeSwitcher.contains(event.target)) {
      closeThemeSwitcher();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeAllDropdowns(null);
      closeThemeSwitcher();
      closeAnnouncementModal();
    }
  });

  /* Announcement lightbox */
  var announcementModal = document.querySelector('.announcement-modal');
  var announcementModalImage = announcementModal && announcementModal.querySelector('.announcement-modal-image');
  var announcementModalTitle = announcementModal && announcementModal.querySelector('.announcement-modal-title');
  var announcementModalClose = announcementModal && announcementModal.querySelector('.announcement-modal-close');
  var announcementButtons = document.querySelectorAll('.announcement-card-button');

  function openAnnouncementModal(imageUrl, title) {
    if (!announcementModal || !announcementModalImage || !announcementModalTitle) {
      return;
    }
    announcementModalImage.src = imageUrl;
    announcementModalImage.alt = title;
    announcementModalTitle.textContent = title;
    announcementModal.classList.add('open');
    announcementModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeAnnouncementModal() {
    if (!announcementModal) {
      return;
    }
    announcementModal.classList.remove('open');
    announcementModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (announcementModalImage) {
      announcementModalImage.src = '';
    }
    if (announcementModalTitle) {
      announcementModalTitle.textContent = '';
    }
  }

  announcementButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      openAnnouncementModal(button.dataset.imageUrl, button.dataset.title);
    });
  });

  if (announcementModal) {
    announcementModal.addEventListener('click', function (event) {
      if (event.target === announcementModal) {
        closeAnnouncementModal();
      }
    });
  }

  if (announcementModalClose) {
    announcementModalClose.addEventListener('click', closeAnnouncementModal);
  }
})();
