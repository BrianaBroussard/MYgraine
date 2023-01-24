'use strict';

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
           
        let trigger_id = responseJson.trigger_id;
        let trigger_name = responseJson.trigger_name;
        let trigger_icon = responseJson.trigger_icon;
        
        document.querySelector('#new-trigger').insertAdjacentHTML('beforeend', `<input type="checkbox" name="triggers" class="btn-check" value=${trigger_id} id=${trigger_name}><label class="btn btn-outline-primary m-1" for=${trigger_name}><span class="material-symbols-outlined">
        ${trigger_icon}
        </span><br>${trigger_name}</label>`);
    }
    });
});


//adds today's date as default value for add headache form
window.addEventListener('DOMContentLoaded', (event) => {
  
  document.getElementById("date-start").valueAsDate = new Date();
  
});



//adds form for medication efficacy and dosage if marked taken
const add_med_button = document.querySelectorAll('.meds');

for (let i=0; i< add_med_button.length; i++) {
  let med_name = add_med_button[i].getAttribute('id')
  let med_id = add_med_button[i].getAttribute('value')
  
  add_med_button[i].addEventListener('click', (event) => {
    if (document.querySelector(`#${med_name}-dose`)) {
      document.querySelector(`#${med_name}-dose`).remove();
    } else {
    document.querySelector("#selected-meds").insertAdjacentHTML('beforeend', `<div id="${med_name}-dose"> <p> <label for="efficacy">Was ${med_name} helpful?:</label> <select name="efficacy-${med_id}" id="efficacy"> <option value="0"> &#128533 Not Sure </option><option value="1"> &#128545 Not Helpful </option><option value="2"> &#128578 Somewhat Helpful </option><option value="3"> &#128512 Helpful </option> </select></p> <p> <label for="dose">How many ${med_name} did you take?: 
    <input type="number" step="0.5" max="10" min="0.5" value="1"  id="dose" name="dose-${med_id}" class="quantity-field border-1 text-center "> </p> </div>`)
}});
};




// adds period date if add date is selected on headache form
const period_button = document.querySelector('#perioddate');

period_button.addEventListener('click', (evt) => {
    evt.preventDefault();

    document.querySelector('#period-date').insertAdjacentHTML('beforeend', 
    '<label for="date-start">When did your last period start?</label> <input id="period-start" type="date" name="period-start" />');
});
