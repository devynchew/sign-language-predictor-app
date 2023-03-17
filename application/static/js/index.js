const body = document.querySelector('body'),
      sidebar = body.querySelector('nav'),
      toggle = body.querySelector(".toggle"),
      modeSwitch = body.querySelector(".toggle-switch"),
      modeText = body.querySelector(".mode-text");


toggle.addEventListener("click" , () =>{
    sidebar.classList.toggle("close");
})

// Select the theme preference from localStorage
const currentTheme = localStorage.getItem("theme");

// If the current theme in localStorage is "dark"...
if (currentTheme == "dark") {
    // ...then use the .dark-theme class
    body.classList.toggle("dark");
}

modeSwitch.addEventListener("click" , () =>{
    body.classList.toggle("dark");
    
    // Let's say the theme is equal to light
    let theme = "light";

    // If the body contains the .dark-theme class...
    if (body.classList.contains("dark")) {
        // ...then let's make the theme dark
        theme = "dark";
        modeText.innerText = "Dark mode";
    }
    else {
        modeText.innerText = "Light mode";
    }
        
    // Then save the choice in localStorage
    localStorage.setItem("theme", theme);
});

