"use strict";

async function deleteEntry(entry) {
  if (entry.dataset.deleting === "true") return;
  entry.dataset.deleting = "true";
  const feedback = document.getElementById("delete-feedback");
  try {
    const response = await fetch(entry.dataset.deleteUrl);
    const result = await response.json();
    if (!response.ok || result.status !== 1) {
      throw new Error(result.message || "Could not delete post");
    }
    // Reload from the server so the empty-list message is also correct.
    window.location.reload();
  } catch (error) {
    feedback.textContent = error.message;
    entry.dataset.deleting = "false";
  }
}

document.querySelectorAll(".entry").forEach((entry) => {
  entry.addEventListener("click", () => deleteEntry(entry));
  entry.addEventListener("keydown", (event) => {
    if (event.target === entry && (event.key === "Enter" || event.key === " ")) {
      event.preventDefault();
      deleteEntry(entry);
    }
  });
});
