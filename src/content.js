const DEFAULT_RULES = [
  // Strip filler openers
  { pattern: /^(please\s+)?(can\s+you\s+)?(kindly\s+)?/i, replacement: "" },
  // Verbose ask patterns
  { pattern: /I was wondering if you could/gi, replacement: "" },
  { pattern: /I would like you to/gi, replacement: "" },
  { pattern: /Could you please/gi, replacement: "" },
  { pattern: /I need you to/gi, replacement: "" },
  // Redundant affirmations
  { pattern: /\bAs an AI\b/gi, replacement: "" },
  { pattern: /\bof course\b/gi, replacement: "" },
];

function applyRules(text, rules) {
  let result = text;
  for (const rule of rules) {
    result = result.replace(new RegExp(rule.pattern), rule.replacement);
  }
  return result.trim().replace(/\s+/g, " "); // clean up extra spaces
}

function injectIntoEditor(newText) {
  const editor = document.querySelector('[contenteditable="true"]');
  if (!editor) return;

  editor.focus();

  // Replace content safely
  editor.innerText = newText;

  // Trigger input event (important for React)
  editor.dispatchEvent(new InputEvent("input", { bubbles: true }));
}


//function injectIntoEditor(newText) {
//  const editor = document.querySelector("textarea");
//  if (!editor) return;

//  editor.focus();
  
  // ChatGPT uses React so we need to trigger it this way
//  const nativeInputSetter = Object.getOwnPropertyDescriptor(
//    window.HTMLTextAreaElement.prototype, "value"
//  ).set;
//  nativeInputSetter.call(editor, newText);
//  editor.dispatchEvent(new Event("input", { bubbles: true }));
//}

// Listen for a keyboard shortcut: Ctrl+Shift+O to optimize
document.addEventListener("keydown", async (e) => {
  if (e.ctrlKey && e.shiftKey && e.key === "O") {
    const editor = document.querySelector('[contenteditable="true"]');
    if (!editor) return;

    const original = editor.innerText;

    // Load user rules from storage, fall back to defaults
    chrome.storage.sync.get("rules", (data) => {
      const userRules = data.rules || DEFAULT_RULES;
      const optimized = applyRules(original, userRules);
      injectIntoEditor(optimized);
      console.log(`Optimized: "${original}" → "${optimized}"`);
    });
  }
});