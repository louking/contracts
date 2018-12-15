// supporting functions for crudapi.py

// adapted from https://select2.org/tagging > Tag properties
function select2_createtag(params) {
    var term = $.trim(params.term);

    if (term === '') {
        return null;
    }

    console.log('term="'+term+'"');
    return {
        id: 0,
        text: term,
        newTag: true // add additional parameters
    }
}
