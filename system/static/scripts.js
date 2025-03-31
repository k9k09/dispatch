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