'use strict';

window.onload = (event) => {
   
    fetch('/api/quotes')
    .then((response) => response.json())
    .then((quoteData) => {
        let quote= quoteData['quote'];
        let author = quoteData['author'];
        document.querySelector('#quote')
                .textContent = `'${quote}' - ${author}`;
                //console.log(quote, author)
    })
    
  };