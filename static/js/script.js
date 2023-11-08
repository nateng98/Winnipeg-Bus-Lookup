// window.onload = function() {
//   const element = document.getElementById('closePopup');
//   element.classList.add('hidden');
// };

document.addEventListener("DOMContentLoaded", function () {
  const openPopupBtn = document.getElementById("openPopup");
  const closePopupBtn = document.getElementById("closePopup");
  const popupContainer = document.getElementById("popupContainer");

  // openPopupBtn.addEventListener("click", function () {
  //   popupContainer.classList.remove("hidden");
  //   console.log("add");
  // });

  closePopupBtn.addEventListener("click", function () {
    popupContainer.classList.add("hidden");
    console.log("delete");
  });
});