'use strict';

fetch('/users-triggers.json')
.then(response => response.json())
.then(responseJson => {

  const data = responseJson.data.map(triggerdata => ({
    x: triggerdata.trigger, y: triggerdata.count,
  }));
  new Chart(document.querySelector('#trigger-chart'), {
    type: 'bar',
    data: {
      datasets: [{
        label: 'Common Triggers',
        data,  // equivalent to data: data
      }],
    },
    options: {
      datasets: {
        bar: {
          // We use a function to automatically set the background color of
          // each bar in the bar chart.
          //
          // There are many other properties that accept functions. For more
          // information see: https://www.chartjs.org/docs/latest/general/options.html#scriptable-options
          backgroundColor: () =>
            // `randomColor` is a JS module we found off GitHub: https://github.com/davidmerfield/randomColor
            // We imported it in templates/chartjs.html
            randomColor(),
        },
      },
      scales: {
          y: {
              suggestedMin: 1,
              suggestedMax: 5
          }
      }
  }
  });
});



