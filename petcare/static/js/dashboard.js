document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll(".dashboard-section");
    const buttons = document.querySelectorAll(".sidebar-btn");

    function openSection(id) {
        // إخفاء كل الأقسام
        sections.forEach(section => {
            section.style.display = "none";
        });

        // إزالة الكلاس active من كل الأزرار
        buttons.forEach(button => {
            button.classList.remove("active");
        });

        // إظهار القسم المطلوب إذا كان موجوداً
        const targetSection = document.getElementById(id);
        if (targetSection) {
            targetSection.style.display = "block";
        }

        // تفعيل الزر الحالي المطابق للقسم
        const targetButton = document.querySelector(`[data-section="${id}"]`);
        if (targetButton) {
            targetButton.classList.add("active");
        }
    }

    // إضافة الحدث عند الضغط على أزرار القائمة
    buttons.forEach(button => {
        button.addEventListener("click", function () {
            const sectionId = this.getAttribute("data-section");
            openSection(sectionId);
        });
    });

    // افتراضياً يتم عرض قسم الـ overview عند تحميل الصفحة أول مرة
    openSection("overview");
});


function moveSlide(button, direction) {
    const carousel = button.closest('.pet-card-carousel');
    const track = carousel.querySelector('.carousel-track');
    const slides = track.querySelectorAll('.carousel-slide');
    
    // معرفة الصورة الحالية
    let currentIndex = parseInt(carousel.getAttribute('data-index') || '0');
    
    currentIndex += direction;
    
    if (currentIndex < 0) {
        currentIndex = slides.length - 1;
    } else if (currentIndex >= slides.length) {
        currentIndex = 0;
    }
    
    carousel.setAttribute('data-index', currentIndex);
    track.style.transform = `translateX(-${currentIndex * 100}%)`;
}

function toggleEditForm(id){

    const form = document.getElementById(
        "edit-form-" + id
    );


    if(form.style.display === "none"){
        form.style.display = "block";
    }
    else{
        form.style.display = "none";
    }

}
console.log("dashboard.js loaded");

document.addEventListener("click", function (e) {
    console.log("SUBMIT FIRED:", e.target); 
        // التحقق إذا كان الضغط على أزرار التصفح الخاصة بقسم My Pets
        const paginationLink = e.target.closest('#mypets .pagination-container a');
        if (paginationLink) {
            e.preventDefault(); // منع إعادة تحميل الصفحة الكاملة
            const url = paginationLink.href;

            // جلب البيانات من الرابط الجديد عبر fetch
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                // تحويل النص القادم إلى عنصر DOM مؤقت
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                // استخراج قسم الـ mypets الجديد من الصفحة المحملة
                const newMyPetsSection = doc.querySelector('#mypets');
                
                if (newMyPetsSection) {
                    // استبدال محتوى قسم mypets الحالي بالمحتوى الجديد
                    document.getElementById('mypets').innerHTML = newMyPetsSection.innerHTML;
                }
            })
            .catch(error => console.error('Error loading page:', error));
        }
    });

// =======================
// AJAX Approve / Restart Final Fix
// =======================

document.addEventListener("submit", function (e) {
    const form = e.target;

    // التأكد أن الـ form يحمل الكلاس المطلوبة
    if (!form.classList.contains("ajax-request-form")) {
        return;
    }

    e.preventDefault(); // منع الانتقال لصفحة الـ JSON بالقوة

    const formData = new FormData(form);
    const csrfInput = form.querySelector("input[name='csrfmiddlewaretoken']");
    const csrftoken = csrfInput ? csrfInput.value : "";

    fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": csrftoken,
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) return;

        const row = form.closest("tr");
        if (!row) return;

        const statusCell = row.querySelector(".status-cell");
        const actionCell = row.querySelector(".action-cell");

        let cls = "pending";
        if (data.status === "Approved") cls = "approved";
        if (data.status === "Rejected") cls = "rejected";

        if (statusCell) {
            statusCell.innerHTML = `<span class="status ${cls}">${data.status}</span>`;
        }
        if (actionCell) {
            actionCell.innerHTML = "—";
        }
    })
    .catch(error => console.error("Error:", error));
});