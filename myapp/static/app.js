document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('checkout-form');
  const button = document.getElementById('pay-button');
  if (form && button) {
    form.addEventListener('submit', () => {
      if (form.checkValidity()) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Sending payment request…';
      }
    });
  }
});
