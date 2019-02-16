$( function() {
    $( "#navigation ul" ).menu();

    // see https://developers.google.com/identity/sign-in/web/server-side-flow
    $( '.ui-button' ).button();
    $( '#signinButton' ).click(function() {
        // signInCallback defined below
        auth2.grantOfflineAccess().then(signInCallback);
    });
});

// callback when sign-in button response received
function signInCallback(authResult) {
  if (authResult['code']) {

    // Hide the sign-in button now that the user is authorized, for example:
    // $('#signinButton').attr('style', 'display: none');

    // Send the code to the server
    $.ajax({
      type: 'POST',
      url: '/_token',
      // Always include an `X-Requested-With` header in every AJAX request,
      // to protect against CSRF attacks.
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      contentType: 'application/octet-stream; charset=utf-8',
      success: function(result) {
        // Handle or verify the server response.
        if (result.authorized) {
            // reload should hide sign-in button and display appropriate navigation
            location.reload();
        } else {
            // reload to show the error message
            location.reload();
        }
      },
      processData: false,
      data: authResult['code']
    });
  } else {
    // There was an error.
    alert( 'error response received from Google' );
  }
}