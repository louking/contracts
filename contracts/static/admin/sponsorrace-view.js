/*
 * Password prototype for creating password from letters, numbers
 *
 * adapted from https://stackoverflow.com/a/26528271/799921
 */
var Password = {

  _pattern : /[a-zA-Z0-9]/,


  _getRandomByte : function()
  {
    // http://caniuse.com/#feat=getrandomvalues
    if(window.crypto && window.crypto.getRandomValues)
    {
      var result = new Uint8Array(1);
      window.crypto.getRandomValues(result);
      return result[0];
    }
    else if(window.msCrypto && window.msCrypto.getRandomValues)
    {
      var result = new Uint8Array(1);
      window.msCrypto.getRandomValues(result);
      return result[0];
    }
    else
    {
      return Math.floor(Math.random() * 256);
    }
  },

  generate : function(length)
  {
    return Array.apply(null, {'length': length})
      .map(function()
      {
        var result;
        while(true)
        {
          result = String.fromCharCode(this._getRandomByte());
          if(this._pattern.test(result))
          {
            return result;
          }
        }
      }, this)
      .join('');
  }

};

// only define afterdatatables if needed
if ( ['/admin/sponsorraces'].includes(location.pathname) ) {

    function sponsorview_link( url, text ) {
        return function(data, type, row, meta) {
            if (type === 'display' && data !== '') {
                return `<a href=${url}?viewkey=${data}>${text}</a>`;
            }
            return data;
        };
    };

    function sponsorrace_configureformbuttons( that, action ) {
        // set buttons for create
        if ( action == 'create' ) {
            that.buttons( 'Create' );

        // set buttons for edit
        } else if ( action == 'edit' ) {
            that.buttons([
                    {
                        text: 'Update View Key',
                        action: function () {
                            var viewkey = Password.generate(16);
                            that.field('viewkey').set(viewkey);
                        }
                    },
                    {
                        text: 'Update',
                        action: function () {
                            that.submit();
                        }
                    },
                ]);

        // set buttons for remove (only other choice)
        } else {
            that.buttons( 'Delete' );
        }
    };

    // set up buttons for edit form after datatables has been initialized
    function afterdatatables() {
        editor.on('open', function( e, mode, action ) {
            var that = this;

            // set up the buttons
            sponsorrace_configureformbuttons( that, action );

            return true;
        });
    }
} // if [].includes(location.pathname)