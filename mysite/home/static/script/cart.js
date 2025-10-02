var updateBtns = document.getElementsByClassName('update-cart');

for (let i = 0; i < updateBtns.length; i++) {
  updateBtns[i].addEventListener('click', function () {
    var productId = this.dataset.product;
    var action = this.dataset.action;

    if (user === 'AnonymousUser') {
       console.log('User not logged in');

      // Hiện alert Bootstrap
      const alertBox = document.getElementById('login-alert');
      alertBox.classList.remove('d-none');
      setTimeout(() => {
      alertBox.classList.add('d-none');
      }, 5000); // 5000 ms = 5 giây
    } else {
      updateUserOrder(productId, action);
    }       
  });
}

function updateUserOrder(productId, action) {
  var url = '/update_item/';
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({ productId: productId, action: action }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log('Updated:', data);
     
      const clickedBtn = document.querySelector(`[data-product="${data.productId}"][data-action="${action}"]`);
        const row = clickedBtn?.closest('tr');

        // Nếu sản phẩm đã bị xoá
        if (data.removed && row) {
            row.remove();
            return;
        }

        // Nếu không bị xoá => cập nhật số lượng và tổng giá sản phẩm
        if (row) {
            const quantityInput = row.querySelector('input[type="number"]');
            const totalPriceSpan = row.querySelector('.total-price');
            const savePriceSpan = row.querySelector('.sale-total');

          
            if (quantityInput) quantityInput.value = data.quantity;
            if (totalPriceSpan) totalPriceSpan.textContent = `$${Number(data.itemTotal).toFixed(2)}`;
            if (savePriceSpan) savePriceSpan.textContent = `SAVE $${Number(data.savedAmount).toFixed(2)}`;

        }
        const quantityInputindetail = document.querySelector(`#quantity-${data.productId}`);
            if (quantityInputindetail) {
                quantityInputindetail.value = data.quantity;
            }
      // Cập nhật số lượng cart ở header
      const cartCount = document.getElementById('cart-count');
      if (cartCount) {
        cartCount.textContent = data.cartTotalItems;
      }
      // Thêm hiệu ứng trượt
      const wrapper = document.getElementById(`wrapper-${data.productId}`);
      if (wrapper) {
        const newLine = document.createElement('div');
        newLine.className = 'cart-line';
        newLine.textContent = `Đã có ${data.quantity} trong giỏ`;
        wrapper.appendChild(newLine);

        const count = wrapper.querySelectorAll('.cart-line').length - 1;
        wrapper.style.transform = `translateY(-${count * 40}px)`;
        wrapper.style.transition = 'transform 0.3s ease-in-out';
      }

      // Cập nhật tổng số tiền (Subtotal + Total)
        const subtotal = document.getElementById('subtotal-amount');
        const total = document.getElementById('total-amount');
        if (subtotal && total) {
            subtotal.textContent = `$${Number(data.orderTotal).toFixed(2)}`;
            total.textContent = `$${Number(data.orderTotal).toFixed(2)}`;
        }
    });
}







// PRODUCT
  // Hàm thay đổi giá trị ô input (không gửi lên server)
  function changeQuantity(productId, delta) {
      const input = document.getElementById(`quantity-${productId}`);
      let currentValue = parseInt(input.value);
      let newValue = currentValue + delta;
      if (newValue < 1) newValue = 1;
      input.value = newValue;
  }

  // Gửi request thêm sản phẩm vào giỏ hàng với số lượng trong input
  document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const productId = this.dataset.product;
      const quantityInput = document.getElementById(`quantity-${productId}`);
      const quantity = parseInt(quantityInput.value);

      fetch('/update_product/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
          productId: productId,
          quantity: quantity
        })
      })
      .then(res => res.json())
      .then(data => {
        alert(`🛒 Added ${data.quantity} item(s) to cart!`);

        const cartCount = document.getElementById('cart-count');
        if (cartCount) {
          cartCount.textContent = data.cartTotalItems;
        }
      })
      .catch(err => console.error('❌ Error:', err));
    });
  });