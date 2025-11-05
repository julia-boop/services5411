// Tablist Functionality
const tabButtons = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        const target = btn.dataset.tab;

        tabButtons.forEach(b => b.classList.remove("active"));
        tabContents.forEach(tc => tc.classList.remove("active"));

        btn.classList.add("active");
        document.getElementById(target).classList.add("active");
    });
});

// Clarification Funtionality
document.querySelectorAll('.switch-container').forEach(container => {
    const yesInput = container.querySelector('input[value="Yes"]');
    const noInput = container.querySelector('input[value="No"]');
    const group = container.closest('.switch-group');
    const clarification = group.querySelector('.clarification');

    if (clarification) {
        yesInput.addEventListener('change', () => {
        clarification.classList.add('visible');
        const input = clarification.querySelector('input, textarea');
        input.required = true;
        });

        noInput.addEventListener('change', () => {
        clarification.classList.remove('visible');
        const input = clarification.querySelector('input, textarea');
        input.required = false;
        input.value = ''; 
        });
    }
});

document.getElementById("submit-btn").addEventListener("click", function () {
    document.getElementById("service-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const form = this;
    const formData = new FormData(form);
    const data = {};
    const errorContainerId = "form-errors";
    document.getElementById(errorContainerId)?.remove();

    const activeTab = document.querySelector(".tab-content.active")?.id;

    const missing = [];

    document.querySelectorAll("#services .switch-group").forEach(group => {
        const parentTab = group.closest(".tab-content");
        if (parentTab && !parentTab.classList.contains("active")) return;

        if (group.offsetParent === null) return;

        const name = group.querySelector("input[type='radio']")?.name;
        const selected = form.querySelector(`input[name="${name}"]:checked`);
        if (!selected) {
            const question = group.querySelector("p")?.innerText || name;
            missing.push(question);
        }
    });

    document.querySelectorAll(`.tab-content#${activeTab} [required]`).forEach(input => {
    if (!input.value.trim()) {
        const label = input.closest("label")?.innerText ||
                    input.getAttribute("placeholder") ||
                    input.name;
        missing.push(label);
    }
    });

    if (missing.length > 0) {
    const errorBox = document.createElement("div");
    errorBox.id = errorContainerId;
    errorBox.style.marginTop = "20px";
    errorBox.style.background = "#fff4f4";
    errorBox.style.border = "1px solid #e99";
    errorBox.style.padding = "15px";
    errorBox.style.borderRadius = "6px";
    errorBox.style.color = "#b30000";
    errorBox.style.fontSize = "0.95rem";

    const title = document.createElement("strong");
    title.innerText = "⚠️ Please complete the following before submitting:";
    const list = document.createElement("ul");
    list.style.margin = "10px 0 0 20px";
    list.style.listStyle = "disc";

    // Remove duplicates for clarity
    [...new Set(missing)].forEach(item => {
        const li = document.createElement("li");
        li.innerText = item;
        list.appendChild(li);
    });

    errorBox.appendChild(title);
    errorBox.appendChild(list);
    form.appendChild(errorBox);
    return;
    }

  // --- Step 4: Prepare form data and submit ---
    data["date"] = new Date().toLocaleDateString("en-US");
    formData.forEach((value, key) => {
    data[key] = value.trim ? value.trim() : value;
    });

    try {
    const res = await fetch("/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    const result = await res.json();

    if (result.status === "success") {
        alert("✅ Form submitted successfully!");
        form.reset();
    } else {
        alert("❌ There was an error submitting the form. Please try again.");
    }
    } catch (err) {
    console.error("Submission error:", err);
    alert("⚠️ Connection error. Please try again.");
    }
    });


});
