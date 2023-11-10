document.addEventListener("DOMContentLoaded", function () {
  const closePopupBtn = document.getElementById("closePopup");
  const popupContainer = document.getElementById("popupContainer");

  closePopupBtn.addEventListener("click", function () {
    popupContainer.classList.add("hidden");
    console.log("delete");
  });
});