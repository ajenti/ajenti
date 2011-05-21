function termSend(data) {
    $.ajax({
      url: '/term-post/' + data,
      type: 'GET'
    });
}

function termGet() {
    $.ajax({
      url: '/term-get',
      type: 'GET',
      success: function(data) {
        x = Base64.decode(data);
        _term.write(x);
        _term_box_element.scrollTop = 9000*9000;
        setTimeout(termGet, 1000);  
      }
    });  
}
