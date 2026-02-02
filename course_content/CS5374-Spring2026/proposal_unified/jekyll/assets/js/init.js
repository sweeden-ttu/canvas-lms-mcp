document.addEventListener('DOMContentLoaded', function() {
  if (typeof renderMathInElement === 'function') {
    renderMathInElement(document.body, { delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '\\(', right: '\\)', display: false }
    ]});
  }
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({ startOnLoad: false });
    document.querySelectorAll('pre.mermaid, pre code.language-mermaid').forEach(function(el) {
      const node = el.tagName === 'CODE' ? el.parentElement : el;
      if (node) mermaid.run({ nodes: [node], suppressErrors: true });
    });
  }
});
