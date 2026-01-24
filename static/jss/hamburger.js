// Hamburger Menu Logic

function toggleMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    const hamburger = document.querySelector('.hamburger');
    const backdrop = document.getElementById('menuBackdrop');

    mobileMenu.classList.toggle('active');
    hamburger.classList.toggle('toggle');
    backdrop.classList.toggle('active');
}

// Close menu when clicking backdrop
document.addEventListener('DOMContentLoaded', () => {
    // Create backdrop if it doesn't exist
    if (!document.getElementById('menuBackdrop')) {
        const backdrop = document.createElement('div');
        backdrop.id = 'menuBackdrop';
        backdrop.className = 'menu-backdrop';
        backdrop.onclick = toggleMenu;
        document.body.appendChild(backdrop);
    }
});
