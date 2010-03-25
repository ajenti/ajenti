function ui_center(el) {
    sw = document.width;
    sh = document.height;
    e = document.getElementById(el);
    e.style.left = (sw / 2 - e.clientWidth / 2) + 'px';
    e.style.top = (sh / 2 - e.clientHeight / 2) + 'px';
}
