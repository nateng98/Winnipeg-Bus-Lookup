document.addEventListener("DOMContentLoaded", function () {
  const closePopupBtn = document.getElementById("closePopup");
  const sqlTable = document.getElementById("myTable");

  closePopupBtn.addEventListener("click", function () {
    sqlTable.classList.add("hidden");
    console.log("delete");
  });
});

// Add a scroll event listener to the table
document.getElementById('myTable').addEventListener('scroll', function (e) {
  // Get the header element
  var thead = this.querySelector('thead');
  // Set the left style property of the header to the negative scrollLeft value
  thead.style.left = '-' + this.scrollLeft + 'px';
});