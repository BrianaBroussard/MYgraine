'use strict';

$(function() {  
    $( "#add-trigger" ).autocomplete({  
     source: function(request, response) {
             $.ajax({
               type: "POST",
               url: "/search-triggers.json",
               dataType: "json",
               data: {
                   q: request.term
             },
               success : function(data) {
                 response(data);
             },

           }
           );
         }, 
         minLength: 1
     });
     }); 
