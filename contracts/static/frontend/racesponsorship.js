// racesponsorship.js

$(function (){
  $('select').formSelect();
  M.AutoInit();

  // this is needed to add ignore-validate classes to hidden fields
  showCurrentInputPage();

});

      var currpagendx = 0;
      var pages = ['sponsordata', 'confirmation', 'payment-wait'];
      var confirmationfields = {};

      // form validation on submit - validates each page
      $('#sponsorform').validate({
//        debug: true,
        submitHandler: nextOrSubmitPage,
        ignore: '.ignore-validate',
        errorClass: "invalid form-error",
        errorElement: 'div',
        errorPlacement: function(error, element) {
          error.appendTo(element.parent());
        },
      });
      
      function nextOrSubmitPage(form) {
      
        console.log('nextOrSubmitPage()');
        
        // send email if at the confirmation page
        if (getCurrentPage() == 'confirmation') {
          sendForm();
          currpagendx += 1;
          showCurrentInputPage();
        
        // go to the next page if not at the last page
        } else {
          if ($('#sponsorform').valid()) {
            currpagendx += 1;
            showCurrentInputPage();
          };
        };

        // jump to top of form - see http://stackoverflow.com/questions/3163615/how-to-scroll-html-page-to-given-anchor-using-jquery-or-javascript
        var scroll_to = document.getElementById('sponsorform');
        scroll_to.scrollIntoView();

      };
      
      function backPage() {
        if (currpagendx > 0) {
          currpagendx -= 1;
          showCurrentInputPage();      
          // jump to top of form - http://stackoverflow.com/questions/3163615/how-to-scroll-html-page-to-given-anchor-using-jquery-or-javascript
          var scroll_to = document.getElementById('sponsorform');
          scroll_to.scrollIntoView();
          
        // hmm, how did this happen?
        } else {
          alert('*** back not permitted at start page');
        };
      };
      
      function getCurrentPage() {
        return pages[currpagendx].replace( '{race}', $('#race').val() );
      };
      
      function showCurrentInputPage () {
        var currpage = getCurrentPage();
        
        // maybe we're looking for confirmation?
        if (currpage == 'confirmation') {
          setConfirmationFields();
          
          // show correct buttons and text
// add paymentoption back when solution / workaround for https://github.com/paypal/paypal-checkout/issues/125 found
//          if (confirmationfields.paymentoption.val != 'paypal') {
          if (true) {
            $('.paypal').hide();
            $('.nopaypal').show();
          } else {
            $('.paypal').show();
            $('.nopaypal').hide();
          };
        };
          
        // show only the current page
        $('.input').hide();
        $('#'+currpage).show();
        
        // show current race
        showRace();
        
        // add ignore-validate class to all hidden page fields we're validating
//        $('.validate').addClass('ignore-validate');
//        $('#'+currpage).removeClass('ignore-validate');
        
        // show the footer for input pages
        if (currpage != 'payment-wait') {
          $('#footer').show();
        };
          
        console.log('showCurrentInputPage(): currpage='+currpage);
      };

      // set sponsor level based on sponsor amount
      function setLevel() {
          console.log('setLevel()');
          
          // this depends on race and amount fields being filled into confirmation fields before level field
          var raceval = $( '#race' ).val();
          var racename = $( '#race option[value=' + raceval + ']').text()

          var amountid = '#' + $('#race').val() + '-amount'
          var levelid = '#' + $('#race').val() + '-level'
          var amount = $( amountid ).val();
          console.log('setLevel(): racename="' + racename + '" amount=' + amount)
            
          // levels sorted high to low
          var levelname = 'ERROR: Amount not high enough for minimum sponsorship';
          for (i=0; i<levels[racename].length; i++) {
            var level = levels[racename][i];
            if (amount >= level.minsponsorship) {
              levelname = level.levelname;
              break;
            };
          };
          // set level name into {race}-level field
          $( levelid ).val(levelname);
          $( levelid ).trigger('autoresize');
      };
      
      // set confirmationfields object, and #confirmation-fields DOM element
      function setConfirmationFields() {
        $('#confirmation-fields *').remove();
        
// add paymentoption back when solution / workaround for https://github.com/paypal/paypal-checkout/issues/125 found
//        var formfields = ['organization', 'name','phone', 'street', 'city', 'state', 'zipcode', 'email', 'race', 'amount', 'level', 'paymentoption', 'comments'];
        var formfields = ['organization', 'name','phone', 'street', 'city', 'state', 'zipcode', 'email', 'race', 'amount', 'level', 'comments'];
        confirmationfields._keyorder = formfields;
        
        for (var i=0; i<formfields.length; i++) {
          var outfield = formfields[i];
          var formfield = outfield;
          
          // special case for amount and level fields
          if (formfield == 'amount') { formfield = $('#race').val() + '-amount' };
          if (formfield == 'level') { formfield = $('#race').val() + '-level' };
          var fieldid = '#' + formfield;
          
          // some special processing depending on tag
          var formtag = $( fieldid ).get(0).tagName; 

          // remember label used on form, replacing ' *' with null (required fields)
          // all but select start at parent, for select start at parent.parent
          var labelsearch = $( fieldid ).parent();
          if (formtag.toLowerCase() == 'select') {
            labelsearch = labelsearch.parent();
          };
          var formlabel = labelsearch.find('label').text().replace(' \*','');
          
          // set text to be the same as val, unless select
          var formval = $( fieldid ).val();
          var formtext = formval
          if (formtag.toLowerCase() == 'select') {
            formtext = $( fieldid + ' option[value=' + formval + ']').text()
          };
          
          // update confirmationfields, which will be used to send data to server
          confirmationfields[outfield] = { val : formval, text : formtext, label : formlabel, tag : formtag };
          
          // add DOM block to #confirmation-fields
          $('#confirmation-fields').append('<div class="row" id="conf-' + outfield + '"></div>');
          var row = $('#conf-' + outfield);
          row.append('<div class="col s6">' + confirmationfields[outfield].label + '</div>');
          row.append('<div class="col s6">' + confirmationfields[outfield].text + '</div>');
        };

        // fill in _racedirector after all other confirmation fields retrieved
        confirmationfields._racedirector = races[confirmationfields.race.text].racedirector;
      };
      
      function showRace() {
        $('.all-races').hide();
        $('#' + $('#race').val() + '-race').show();
        $('.all-races input').addClass('ignore-validate');
        $('#' + $('#race').val() + '-race input').removeClass('ignore-validate');
        $('.amount-fields').show();
      };

      function getFormData() {
        return confirmationfields;
      };
      
      function sendForm() {
        console.log('sendForm()');
        var formdata = getFormData();
        // formdata = {};
        // formdata._keyorder = confirmfields._keyorder;
        // for (i=0; i<formdata._keyorder.length; i++) {
        //   field = formdata._keyorder[i];
        //   formdata[field] = confirmfields[field].text;
        // }
        $.post({
                url: window.location.href, 
                data: {json:JSON.stringify(formdata)}, 
                success: showFormSuccess,
        })
      }

      function showFormSuccess(e) {
        console.log('showSuccess('+e+')');
        if (e === "OK") { 
          $('.input').hide();
          $('#success').show();
        } else {
          showError(e);
        }
      }

      function showError(e) {
        $('#error-notification').append('<p style="font-style:italic;">Error details: '+e+'</p>');
        $('#error-notification').show();
      }


// adapted from https://developer.paypal.com/docs/integration/direct/express-checkout/integration-jsv4/basic-integration/

// add back when paypal available waiting on https://github.com/paypal/paypal-checkout/issues/125
//    paypal.Button.render({
//    
//        env: 'sandbox', // specify 'production' or 'sandbox' environment
//    
//        client: {
//            sandbox:    'AeaekqhkrW1cF3Y59_8dpu8BrX-7vLHJpvuXvRVAZfLhBezHHe0ofbbRbf8YIlxKE6xiWLBzeqPFdZnF',
//            production: 'AUydf6IqW8dNCJvXum8cQzc_Is2KaTBIAmyQAlFuFT1gKuBfYyWU059iGe7fClHCvNVS3tPOEljlgwuT'
//        },
//
//        payment: function() {
//        
//            var env    = this.props.env;
//            var client = this.props.client;
//            
//            return paypal.rest.payment.create(env, client, {
//                transactions: [
//                    {
//                        amount: { total: confirmationfields.amount.val, 
//                                  currency: 'USD' }
//                    }
//                ]
//            });
//        },
//
//        commit: true, // Optional: show a 'Pay Now' button in the checkout flow
//
//        onAuthorize: function(data, actions) {
//        
//            // Optional: display a confirmation page here
//        
//            return actions.payment.execute().then(function() {
//                // Show a success page to the buyer
//                sendForm();
//            });
//        },
//        
//        onCancel: function(data) {
//          backPage();
//        },
//
//    }, '#paypal-button');

