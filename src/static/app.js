document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsHtml = details.participants && details.participants.length
          ? `<p><strong>Participants:</strong></p>
             <ul class="participants-list">
               ${details.participants.map(p => {
                 const username = p.split("@")[0];
                 return `<li><span class="participant-email">${username}</span><button class="delete-participant" data-activity="${name}" data-email="${p}" aria-label="Remove ${p}">✕</button></li>`;
               }).join("")}
             </ul>`
          : `<p class="no-participants">No participants yet</p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHtml}
        `;

        // Add click handlers to delete buttons
        activitiesList.querySelectorAll(".delete-participant").forEach(button => {
          button.addEventListener("click", async (e) => {
            e.preventDefault();
            const activityName = button.getAttribute("data-activity");
            const email = button.getAttribute("data-email");

            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(email)}`,
                {
                  method: "DELETE",
                }
              );

              if (response.ok) {
                // Refresh activities to reflect changes
                fetchActivities();
              } else {
                const result = await response.json();
                alert(result.detail || "Failed to remove participant");
              }
            } catch (error) {
              alert("Failed to remove participant. Please try again.");
              console.error("Error removing participant:", error);
            }
          });
        });

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown if not already present
        const existingOption = Array.from(activitySelect.options).find(o => o.value === name);
        if (!existingOption) {
          const option = document.createElement("option");
          option.value = name;
          option.textContent = name;
          activitySelect.appendChild(option);
        }
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities to show the new signup
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
