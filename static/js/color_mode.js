'use strict'
let preferredTheme = "light";

const colorToggle = document.querySelector('#color-toggle');

colorToggle.addEventListener('click',()=>{
    
    if (document.documentElement.getAttribute('data-bs-theme') === 'dark') {
        document.documentElement.setAttribute('data-bs-theme', 'light');
        preferredTheme = "light";
        localStorage.setItem("preferredTheme", preferredTheme); 
    }
    else {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
        preferredTheme = "dark";
        localStorage.setItem("preferredTheme", preferredTheme);
           
    }
});

let theme = localStorage.getItem("preferredTheme")

window.addEventListener('DOMContentLoaded', () => {
    document.documentElement.setAttribute('data-bs-theme', theme);
    if (theme === "dark") {
        colorToggle.setAttribute('checked', "");
        
    } 
});


