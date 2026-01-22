/**
 * background-particles.js
 * Creates a stunning constellation/particle network background effect.
 * Automatically adapts to the current theme colors.
 */

(function () {
    // 1. Setup Canvas
    const canvas = document.createElement('canvas');
    canvas.id = 'particle-canvas';
    Object.assign(canvas.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100%',
        height: '100%',
        zIndex: '-1', // Behind content but likely in front of background-color/blobs
        pointerEvents: 'none' // Click-through
    });
    document.body.prepend(canvas);

    const ctx = canvas.getContext('2d');
    let width, height;
    let particles = [];

    // Configuration
    const particleCount = window.innerWidth < 768 ? 40 : 100; // Increased count
    const connectionDist = 150;
    const mouseDist = 200;

    // Election vocabulary for nodes
    const vocabulary = "VOTE ELECTION SECURE DEMOCRACY BLOCKCHAIN RVCE 2025".split(" ");
    const letters = vocabulary.join("").split("");

    // Theme Colors (will be updated dynamically)
    let particleColor = 'rgba(255, 255, 255, 0.5)';
    let lineColor = 'rgba(255, 255, 255, 0.15)';

    // ... (resize logic same) ...
    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    // 2. Mouse Interaction
    const mouse = { x: null, y: null };
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });
    window.addEventListener('mouseleave', () => {
        mouse.x = null;
        mouse.y = null;
    });

    // 3. Particle Class
    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.3; // Slower, more elegant
            this.vy = (Math.random() - 0.5) * 0.3;
            this.size = Math.random() * 2 + 1;

            // 30% chance to be a letter node
            this.isLetter = Math.random() > 0.7;
            this.char = letters[Math.floor(Math.random() * letters.length)];
            this.angle = (Math.random() - 0.5) * 0.5; // Slight rotation for letters
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            // Bounce off edges
            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;

            // Mouse interaction (repel)
            if (mouse.x != null) {
                let dx = mouse.x - this.x;
                let dy = mouse.y - this.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < mouseDist) {
                    const forceDirectionX = dx / distance;
                    const forceDirectionY = dy / distance;
                    const force = (mouseDist - distance) / mouseDist;
                    const directionX = forceDirectionX * force * 3;
                    const directionY = forceDirectionY * force * 3;
                    this.x -= directionX;
                    this.y -= directionY;
                }
            }
        }

        draw() {
            ctx.fillStyle = particleColor;

            if (this.isLetter) {
                ctx.font = "bold 14px 'Poppins', sans-serif";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText(this.char, this.x, this.y);
            } else {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }

    // 4. Initialize Particles
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    // 5. Update Colors based on Theme
    function updateThemeColors() {
        const isLight = document.documentElement.getAttribute('data-theme') === 'light';
        if (isLight) {
            particleColor = 'rgba(79, 70, 229, 0.4)'; // Indigo-ish for light mode
            lineColor = 'rgba(79, 70, 229, 0.1)';
        } else {
            particleColor = 'rgba(255, 255, 255, 0.3)';
            lineColor = 'rgba(255, 255, 255, 0.05)';
        }
    }

    // Observer for theme changes
    const observer = new MutationObserver(updateThemeColors);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    updateThemeColors(); // Initial set

    // 6. Animation Loop
    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Draw and update particles
        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            // Connect lines
            for (let j = i; j < particles.length; j++) {
                let dx = particles[i].x - particles[j].x;
                let dy = particles[i].y - particles[j].y;
                let distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < connectionDist) {
                    ctx.beginPath();
                    ctx.strokeStyle = lineColor;
                    ctx.lineWidth = 1;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }

    animate();
})();
