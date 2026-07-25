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

  var header = document.querySelector('.site-header');
  function updateHeaderState() {
    if (header) {
      header.classList.toggle('scrolled', window.scrollY > 8);
    }
  }
  updateHeaderState();
  window.addEventListener('scroll', updateHeaderState, { passive: true });

  var heroVisual = document.querySelector('.hero-visual');
  var heroPanel = document.querySelector('.hero-panel');
  if (heroVisual && heroPanel) {
    heroVisual.addEventListener('mousemove', function (event) {
      var rect = heroVisual.getBoundingClientRect();
      var x = ((event.clientX - rect.left) / rect.width - 0.5) * 10;
      var y = ((event.clientY - rect.top) / rect.height - 0.5) * 10;
      heroPanel.style.transform = 'perspective(900px) rotateY(' + (x * -0.7).toFixed(2) + 'deg) rotateX(' + (y * 0.5).toFixed(2) + 'deg) translateY(-4px)';
    });
    heroVisual.addEventListener('mouseleave', function () {
      heroPanel.style.transform = '';
    });
  }

  var revealItems = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
  revealItems.forEach(function (item, index) {
    item.style.setProperty('--reveal-index', index);
    item.style.transitionDelay = (index * 70) + 'ms';
  });

  function revealOnScroll() {
    revealItems.forEach(function (item) {
      var rect = item.getBoundingClientRect();
      if (rect.top < window.innerHeight - 110) {
        item.classList.add('is-visible');
      }
    });
  }
  revealOnScroll();
  if ('IntersectionObserver' in window) {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.18 });
    revealItems.forEach(function (item) {
      revealObserver.observe(item);
    });
  } else {
    window.addEventListener('scroll', revealOnScroll, { passive: true });
    window.addEventListener('resize', revealOnScroll);
  }

  /* ---------------------------------------------------------------
   * Mobile nav drawer toggle
   * ------------------------------------------------------------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("main-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      document.body.classList.toggle("nav-open", isOpen);
      if (!isOpen) {
        closeAllDropdowns(null);
      }
    });
  }

  var backdrop = document.querySelector('.nav-backdrop');
  if (backdrop) {
    backdrop.addEventListener('click', function () {
      if (nav) {
        nav.classList.remove('open');
        toggle && toggle.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('nav-open');
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
        var firstLink = item.querySelector(".dropdown-menu a, .dropdown-menu button");
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

// ---- Copy article link (news detail share row) ----
(function () {
  document.querySelectorAll('[data-copy-link]').forEach(function (button) {
    button.addEventListener('click', function () {
      var url = button.getAttribute('data-copy-link');
      var reset = function () {
        button.removeAttribute('data-copied');
      };
      var done = function () {
        button.setAttribute('data-copied', 'true');
        button.setAttribute('aria-label', 'پیوند کپی شد');
        setTimeout(function () {
          button.setAttribute('aria-label', 'کپی پیوند خبر');
          reset();
        }, 1800);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done).catch(function () {});
      } else {
        var temp = document.createElement('textarea');
        temp.value = url;
        document.body.appendChild(temp);
        temp.select();
        try { document.execCommand('copy'); done(); } catch (e) {}
        document.body.removeChild(temp);
      }
    });
  });
})();
