


const button = document.querySelector('#periodtrue');

function handleClick() {
    document.querySelector('#period-yes').insertAdjacentHTML('beforeend', 
    '<label for="date-start">When did your period start?</label> <input id="period-start" type="datetime-local" name="period-start" />');
}

button.addEventListener('click', handleClick);



