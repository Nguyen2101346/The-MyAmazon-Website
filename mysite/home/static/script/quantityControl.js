// function increase() {
//       const input = document.getElementById('quantity');
//       input.value = parseInt(input.value) + 1;
//     }

// function decrease() {
//     const input = document.getElementById('quantity');
//     const value = parseInt(input.value);
//     if (value > 1) {
//     input.value = value - 1;
//     }
// }

document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll('.add-to-cart-btn');

  buttons.forEach(button => {
    const wrapper = button.querySelector('.text-wrapper');

    button.addEventListener('click', function () {
      const productId = this.dataset.product;
      const action = this.dataset.action;

      updateUserOrder(productId, action, this);
    });
  });
});