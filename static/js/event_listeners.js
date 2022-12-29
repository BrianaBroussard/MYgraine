
// adds period date if add date is selected on headache form
const button = document.querySelector('#perioddate');

button.addEventListener('click', (evt) => {
    evt.preventDefault();

    document.querySelector('#period-date').insertAdjacentHTML('beforeend', 
    '<label for="date-start">When did your last period start?</label> <input id="period-start" type="datetime-local" name="period-start" />');
});



