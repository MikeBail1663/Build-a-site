document.addEventListener('DOMContentLoaded', function () {
    const circles = document.querySelectorAll('.progress-circle');
    circles.forEach(circle => {
        const complete = parseInt(circle.getAttribute('data-complete'));
        const goal = parseInt(circle.getAttribute('data-goal'));
        const percentage = Math.min((complete / goal) * 100, 100);

        circle.style.background = `conic-gradient(#4caf50 ${percentage}%, #ccc ${percentage}%)`;
    });
});
