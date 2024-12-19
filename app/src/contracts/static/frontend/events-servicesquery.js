  $(document).ready(function(){
    $('select').formSelect();
    // see https://stackoverflow.com/a/40124502/799921
    $("select[required]").css({display: "block", height: 0, padding: 0, width: 0, position: 'absolute', left: '50%'});
  });