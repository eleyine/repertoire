$( document ).ready(function() {

  utils = (function () {
      return {
          escapeRegExChars: function (value) {
              return value.replace(/[|\\{}()[\]^$+*?.]/g, "\\$&");
          },
          createNode: function (containerClass) {
              var div = document.createElement('div');
              div.className = containerClass;
              div.style.position = 'absolute';
              div.style.display = 'none';
              return div;
          }
      };
  }()),

  $.getJSON( "/api/lookup", function( protocols ) {
    console.log("hey my dude");

    $('#protocols-autocomplete').autocomplete({
        lookup: protocols,
        groupBy: 'category',
        onSelect: function (suggestion) {
          // $('#protocols-autocomplete').val(suggestion.data.category);
          this.value = suggestion.data.category;
          window.location.href = suggestion.data.url;
        },
        formatResult: function (suggestion, currentValue) {
          if (!currentValue) {
              return suggestion.data.field;
          }

          var pattern = '(' + utils.escapeRegExChars(currentValue) + ')';
          return suggestion.data.field
              .replace(new RegExp(pattern, 'gi'), '<strong>$1<\/strong>')
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/&lt;(\/?strong)&gt;/g, '<$1>');
        }
    });
  });


});
