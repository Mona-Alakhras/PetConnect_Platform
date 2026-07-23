 document.addEventListener("DOMContentLoaded", function () {
        const filterButtons = document.querySelectorAll(".filter-btn");
        const petCards = document.querySelectorAll(".browse-card");
        const noPetsMessage = document.getElementById("no-pets-message");

        filterButtons.forEach(button => {
            button.addEventListener("click", () => {
                filterButtons.forEach(btn => btn.classList.remove("active"));
                button.classList.add("active");

                const filterValue = button.getAttribute("data-filter");
                let visibleCount = 0;

                petCards.forEach(card => {
                    const cardCategory = card.getAttribute("data-category");

                    if (filterValue === "all" || (cardCategory && cardCategory.toLowerCase() === filterValue.toLowerCase())) {
                        card.style.display = "flex";
                        visibleCount++;
                    } else {
                        card.style.display = "none";
                    }
                });

                // إظهار أو إخفاء الرسالة بناءً على عدد النتائج
                if (visibleCount === 0) {
                    noPetsMessage.style.display = "block";
                } else {
                    noPetsMessage.style.display = "none";
                }
            });
        });
    });