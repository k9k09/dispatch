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
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    lucide.createIcons();

    // Navigation handling
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));
            // Add active class to clicked item
            item.classList.add('active');
        });
    });

    // Search functionality
    const searchInput = document.querySelector('input[type="text"]');
    searchInput.addEventListener('input', (e) => {
        // Add your search logic here
        console.log('Searching for:', e.target.value);
    });

    // Notification button
    const notificationBtn = document.querySelector('button i[data-lucide="bell"]').parentElement;
    notificationBtn.addEventListener('click', () => {
        // Add your notification logic here
        console.log('Notifications clicked');
    });

    // Book Now buttons
    const bookButtons = document.querySelectorAll('a:contains("Book Now")');
    bookButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            // Optional: Add confirmation or additional booking logic here
            console.log('Booking bike:', e.target.closest('.bg-white').querySelector('h3').textContent);
        });
    });
});


