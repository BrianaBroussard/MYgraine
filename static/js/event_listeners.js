'use strict';

// adds period date if add date is selected on headache form
const period_button = document.querySelector('#perioddate');

period_button.addEventListener('click', (evt) => {
    evt.preventDefault();

    document.querySelector('#period-date').insertAdjacentHTML('beforeend', 
    '<label for="date-start">When did your last period start?</label> <input id="period-start" type="datetime-local" name="period-start" />');
});


// adds trigger button if user clicks
const add_trigger_button = document.querySelector('#add-trigger-button');

add_trigger_button.addEventListener('click', (event) => {
    event.preventDefault();

 const formInputs = {
    trigger: document.querySelector('#add-trigger').value,
  };

  fetch('/add-trigger.json', {
    method: 'POST',
    body: JSON.stringify(formInputs),
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((response) => response.json())
    .then((responseJson) => {
        
        if (responseJson.status === "Error") {
            alert("Sorry that trigger is already listed");
        } else {
        alert(responseJson.status);    
        let trigger_id = responseJson.trigger_id;
        let trigger_name = responseJson.trigger_name;
        
        document.querySelector('#new-trigger').insertAdjacentHTML('beforeend', `<input type="checkbox" name="triggers" value=${trigger_id} id=${trigger_name}><label for=${trigger_name}>${trigger_name}</label>`);
    }
    });
});


