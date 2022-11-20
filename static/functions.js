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

