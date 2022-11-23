function show_element_hide_element(show_dev, hide_dev) {
    var to_show = document.getElementById(show_dev);
    var to_hide = document.getElementById(hide_dev);
    if (to_show.style.display === "none") {
        to_show.style.display = "block";
        to_hide.style.display = "none";
    } else {
        to_show.style.display = "none";
        to_hide.style.display = "block";
    }
}

function increaseValue() {
    var value = parseInt(document.getElementById('cache_capcity').value, 10);
    value = isNaN(value) || value > 8 ? 8 : value;
    if(!(value >= 8)) value++;
    document.getElementById('cache_capcity').value = value;
  }
  
  function decreaseValue() {
    var value = parseInt(document.getElementById('cache_capcity').value, 10);
    value = isNaN(value) || value < 1 ? 1 : value;
    if(!(value <= 1)) value--;
    document.getElementById('cache_capcity').value = value;
  }
