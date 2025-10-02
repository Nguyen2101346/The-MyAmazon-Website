
const avatarInput = document.getElementById('avatarInput');
const avatarImage = document.getElementById('avatarImage');
const changeBtn = document.getElementById('changeBtn');
const avatarBox = document.getElementById('avatarBox');
const avatarPreview = document.getElementById('avatarPreview');

// Nhấn nút + để mở hộp thoại chọn ảnh
changeBtn.addEventListener('click', (e) => {
  avatarInput.click();
});

// Khi người dùng chọn ảnh từ file explorer
avatarInput.addEventListener('change', function () {
  if (this.files && this.files[0]) {
    previewImage(this.files[0]);
  }
});

// Kéo ảnh vào khung để thay đổi avatar
['dragenter', 'dragover'].forEach(evt => {
  avatarBox.addEventListener(evt, (e) => {
    e.preventDefault();
    avatarPreview.classList.add('drag-over');
  });
});

['dragleave', 'drop'].forEach(evt => {
  avatarBox.addEventListener(evt, (e) => {
    e.preventDefault();
    avatarPreview.classList.remove('drag-over');
  });
});

// Xử lý khi thả ảnh vào khung
avatarBox.addEventListener('drop', (e) => {
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) {
    previewImage(file);
  }
});

// Hàm xem trước ảnh
function previewImage(file) {
  const reader = new FileReader();
  reader.onload = function (e) {
    avatarImage.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

