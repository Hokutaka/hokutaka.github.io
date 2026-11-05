/* Progressive enhancement: without JavaScript, every note remains visible. */
(() => {
  const filters = document.querySelector("[data-notes-filters]");
  const list = document.querySelector("#notes-list");
  if (!filters || !list) return;

  const buttons = Array.from(filters.querySelectorAll("[data-notes-filter]"));
  const notes = Array.from(list.querySelectorAll("[data-note-tags]"));
  const empty = document.querySelector("#notes-filter-empty");
  const supported = new Set(["all", "video", "program"]);

  function currentTag() {
    const tag = window.location.hash.slice(1);
    return supported.has(tag) ? tag : "all";
  }

  function render(tag) {
    let visibleCount = 0;

    for (const note of notes) {
      const tags = note.dataset.noteTags.split(",").filter(Boolean);
      const visible = tag === "all" || tags.includes(tag);
      note.hidden = !visible;
      if (visible) visibleCount += 1;
    }

    for (const button of buttons) {
      button.setAttribute("aria-pressed", String(button.dataset.notesFilter === tag));
    }

    if (empty) empty.hidden = visibleCount !== 0;
  }

  for (const button of buttons) {
    button.addEventListener("click", () => {
      const tag = button.dataset.notesFilter;
      if (!supported.has(tag)) return;

      const url = window.location.pathname + window.location.search + (tag === "all" ? "" : "#" + tag);
      window.history.replaceState(null, "", url);
      render(tag);
    });
  }

  filters.hidden = false;
  render(currentTag());
  window.addEventListener("hashchange", () => render(currentTag()));
  window.addEventListener("popstate", () => render(currentTag()));
})();
