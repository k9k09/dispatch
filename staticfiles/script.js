// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });
  
  // Mobile menu functionality can be added here if needed
  
  // Smooth scroll for navigation links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });
  
  // Mobile menu functionality
  document.addEventListener('DOMContentLoaded', function() {
    // Add hamburger menu button to the DOM
    const nav = document.querySelector('nav .nav-container');
    const navLinks = document.querySelector('.nav-links');
    
    const hamburger = document.createElement('div');
    hamburger.classList.add('hamburger-menu');
    hamburger.innerHTML = `
      <span></span>
      <span></span>
      <span></span>
    `;
    
    nav.appendChild(hamburger);
    
    // Toggle mobile menu
    hamburger.addEventListener('click', function() {
      navLinks.classList.toggle('active');
      hamburger.classList.toggle('active');
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
      if (!event.target.closest('.nav-links') && 
          !event.target.closest('.hamburger-menu') && 
          navLinks.classList.contains('active')) {
        navLinks.classList.remove('active');
        hamburger.classList.remove('active');
      }
    });
  });