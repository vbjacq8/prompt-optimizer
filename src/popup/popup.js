const input = document.getElementById("rules-input");
const saveBtn = document.getElementById("save");

// Load existing rules
chrome.storage.sync.get("rules", (data) => {
  if (data.rules) {
    input.value = JSON.stringify(data.rules, null, 2);
  }
});

saveBtn.addEventListener("click", () => {
  try {
    const rules = JSON.parse(input.value);
    chrome.storage.sync.set({ rules }, () => {
      saveBtn.textContent = "Saved ✓";
      setTimeout(() => (saveBtn.textContent = "Save Rules"), 1500);
    });
  } catch {
    alert("Invalid JSON — check your rules format");
  }
});