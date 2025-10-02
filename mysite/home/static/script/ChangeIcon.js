  const collapseOne = document.getElementById('collapseOne');
  const icon = document.getElementById('voucherIcon');

  collapseOne.addEventListener('show.bs.collapse', () => {
    icon.classList.add('active');
  });

  collapseOne.addEventListener('hide.bs.collapse', () => {
    icon.classList.remove('active');
  });