/**
 * cursor.js -> ui-polish.js
 * Features:
 * 1. Scroll Reveal Animations (Fade in on scroll)
 * 2. Subtle 3D Tilt (Retained but optimized)
 * 3. NO CUSTOM CURSOR (Removed per user request)
 */

document.addEventListener('DOMContentLoaded', () => {
    initScrollReveal();
    // Only init Tilt on Desktop to save mobile resources
    if (window.matchMedia("(pointer: fine)").matches) {
        initUniversalTilt();
    }
});

function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    // Target major layout elements
    const elements = document.querySelectorAll('.option-card, .result-card, .welcome-card, .winner-box, .explainer-card, h1, .subtitle');
    elements.forEach(el => {
        el.classList.add('reveal-on-scroll');
        observer.observe(el);
    });
}

function initUniversalTilt() {
    // simple lightweight 3D tilt
    const cards = document.querySelectorAll('.option-card, .result-card, .welcome-card, .winner-box, .explainer-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -5; // Max 5deg rotation
            const rotateY = ((x - centerX) / centerX) * 5;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        });

        // Add smooth transition for the reset, but remove it during movement for performance
        card.style.transition = 'transform 0.1s ease-out';
    });
}
