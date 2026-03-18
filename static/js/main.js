document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('nav a');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    const form = document.getElementById('verify-form');
    if (form) {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            const userId = document.getElementById('user_id').value;
            const submittedData = document.getElementById('submitted_data').value;
            try {
                const response = await fetch('/api/verify-identity', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ user_id: userId, submitted_data: JSON.parse(submittedData) })
                });
                const result = await response.json();
                alert(`Verification request submitted with ID: ${result.request_id}`);
            } catch (error) {
                console.error('Error submitting verification:', error);
            }
        });
    }

    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
});
