/**
 * stars.js — Interactive star rating picker
 * Handles hover, click, and form submission state for all .star-picker elements.
 * No dependencies — vanilla JS only.
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Star Pickers ───────────────────────────────────────────────────────────
  document.querySelectorAll('.star-picker').forEach(picker => {
    const targetId = picker.dataset.target;
    const hiddenInput = document.getElementById(targetId);
    const stars = Array.from(picker.querySelectorAll('.star-btn'));

    // Find the submit button within the same form
    const form = picker.closest('form');
    const submitBtn = form ? form.querySelector('button[type="submit"]') : null;

    // Current selected value (may be pre-filled for update forms)
    let currentValue = parseInt(hiddenInput.value) || 0;

    function paintStars(upTo) {
      stars.forEach((star, i) => {
        if (i < upTo) {
          star.classList.add('star-btn--active');
          star.classList.remove('star-btn--hover');
        } else {
          star.classList.remove('star-btn--active');
          star.classList.remove('star-btn--hover');
        }
      });
    }

    function hoverStars(upTo) {
      stars.forEach((star, i) => {
        star.classList.toggle('star-btn--hover', i < upTo && i >= currentValue);
        star.classList.toggle('star-btn--active', i < currentValue);
      });
    }

    // Hover in
    stars.forEach((star, index) => {
      star.addEventListener('mouseenter', () => hoverStars(index + 1));
    });

    // Hover out — restore selected state
    picker.addEventListener('mouseleave', () => paintStars(currentValue));

    // Click — select value
    stars.forEach((star, index) => {
      star.addEventListener('click', () => {
        currentValue = index + 1;
        hiddenInput.value = currentValue;
        paintStars(currentValue);

        // Enable submit button if it was disabled
        if (submitBtn) {
          submitBtn.disabled = false;
        }
      });
    });

    // Initialise with pre-filled value (for update forms)
    if (currentValue > 0) {
      paintStars(currentValue);
    }
  });

  // ── Rating Distribution Bars ───────────────────────────────────────────────
  // The bars need real vote-count-per-star data.
  // We read from data attributes injected by the template (via inline script below).
  // If the data isn't present, the bars stay at 0% width.
  const distBars = document.querySelectorAll('.dist-bar[data-star]');
  if (distBars.length > 0 && window.ratingCounts) {
    const total = parseInt(distBars[0].dataset.total) || 1;
    distBars.forEach(bar => {
      const star = bar.dataset.star;
      const count = window.ratingCounts[star] || 0;
      const pct = total > 0 ? (count / total) * 100 : 0;
      // Animate on next paint
      requestAnimationFrame(() => {
        bar.style.width = pct + '%';
      });
    });
  }

  // ── Auto-dismiss Messages ─────────────────────────────────────────────────
  document.querySelectorAll('.message').forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity .4s';
      msg.style.opacity = '0';
      setTimeout(() => msg.remove(), 400);
    }, 5000);
  });

});
