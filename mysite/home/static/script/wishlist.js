document.addEventListener("DOMContentLoaded", function () {
  // Xử lý click
  document.querySelectorAll(".addwishlist-btn").forEach(btn => {
    btn.addEventListener("click", function () {
      const icon = this.querySelector(".wishlist-icon");
      const productId = this.dataset.product;

      fetch(`/add-to-wishlist/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ product_id: productId })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === "added") {
          icon.classList.add("active");
          this.classList.add("active");

          icon.classList.add("shake");
          setTimeout(() => icon.classList.remove("shake"), 600);

          if (icon.dataset.shakeIntervalId) {
            clearInterval(icon.dataset.shakeIntervalId);
          }

          const intervalId = setInterval(() => {
            icon.classList.add("shake");
            setTimeout(() => icon.classList.remove("shake"), 600);
          }, 3000);

          icon.dataset.shakeIntervalId = intervalId;
        } else if (data.status === "removed") {
          icon.classList.remove("active");
          this.classList.remove("active");

          if (icon.dataset.shakeIntervalId) {
            clearInterval(icon.dataset.shakeIntervalId);
            delete icon.dataset.shakeIntervalId;
          }
        }
      });
    });
  });

  // Khi load, áp dụng hiệu ứng rung cho icon đã active
  document.querySelectorAll(".wishlist-icon.active").forEach(icon => {
    icon.classList.add("shake");
    setTimeout(() => icon.classList.remove("shake"), 600);

    const intervalId = setInterval(() => {
      icon.classList.add("shake");
      setTimeout(() => icon.classList.remove("shake"), 600);
    }, 3000);

    icon.dataset.shakeIntervalId = intervalId;
  });
});
