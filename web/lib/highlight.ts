// 極簡 Python 語法上色（無外部依賴）。輸出已跳脫 HTML，可安全 dangerouslySetInnerHTML。
const KEYWORDS = new Set([
  "def", "return", "import", "from", "as", "if", "elif", "else", "for", "while", "in", "not", "and", "or", "is",
  "None", "True", "False", "lambda", "class", "with", "try", "except", "raise", "pass", "yield", "assert",
]);

export function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

const TOKEN = /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')|(\b\d+(?:\.\d+)?(?:e-?\d+)?\b)|(\b[A-Za-z_]\w*\b)/g;

export function highlightPython(code: string): string {
  let out = "";
  let last = 0;
  let afterDef = false;
  for (const m of code.matchAll(TOKEN)) {
    const idx = m.index ?? 0;
    out += escapeHtml(code.slice(last, idx));
    const [text, com, str, num, ident] = m;
    if (com) out += `<span class="tok-com">${escapeHtml(text)}</span>`;
    else if (str) out += `<span class="tok-str">${escapeHtml(text)}</span>`;
    else if (num) out += `<span class="tok-num">${escapeHtml(text)}</span>`;
    else if (ident) {
      if (KEYWORDS.has(ident)) {
        out += `<span class="tok-kw">${ident}</span>`;
        afterDef = ident === "def";
      } else if (afterDef) {
        out += `<span class="tok-fn">${ident}</span>`;
        afterDef = false;
      } else out += escapeHtml(text);
    } else out += escapeHtml(text);
    last = idx + text.length;
  }
  return out + escapeHtml(code.slice(last));
}
