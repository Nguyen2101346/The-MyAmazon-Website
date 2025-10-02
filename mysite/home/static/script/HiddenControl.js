// My shop
  document.getElementById("toggleApartment").addEventListener("click", function (e) {
    e.preventDefault(); // Ngăn không cho nhảy trang
    // Ẩn nút + Add Apartment
    this.style.display = "none";

    // Hiện form nhập
    document.getElementById("apartmentForm").style.display = "block";
  });

  document.getElementById('noteCheckbox').addEventListener('change', function () {
    const textarea = document.getElementById('noteTextarea');
    textarea.style.display = this.checked ? 'block' : 'none';
  });


  