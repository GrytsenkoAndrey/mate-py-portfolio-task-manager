/* Task Manager — UI behaviour for static mockups.
   Everything here is progressive: in Django most actions become
   normal form POSTs, the JS only adds instant feedback. */
(() => {
  "use strict";

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  /* ---------- Active link in sidebar ---------- */
  const page = location.pathname.split("/").pop() || "index.html";
  const section = document.body.dataset.section;
  $$(".tm-nav a").forEach(a => {
    const href = a.getAttribute("href");
    if (href === page || (section && a.dataset.section === section)) a.classList.add("active");
  });

  /* ---------- Toast ---------- */
  function toast(message) {
    let wrap = $("#toast-wrap");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.id = "toast-wrap";
      wrap.className = "toast-container position-fixed bottom-0 end-0 p-3";
      document.body.appendChild(wrap);
    }
    const el = document.createElement("div");
    el.className = "toast align-items-center bg-white";
    el.setAttribute("role", "status");
    el.innerHTML = `<div class="d-flex"><div class="toast-body">${message}</div>
      <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Закрыть"></button></div>`;
    wrap.appendChild(el);
    const t = new bootstrap.Toast(el, { delay: 2500 });
    el.addEventListener("hidden.bs.toast", () => el.remove());
    t.show();
  }
  window.tmToast = toast;

  /* ---------- Clickable table rows ---------- */
  document.addEventListener("click", e => {
    const row = e.target.closest("tr[data-href]");
    if (!row || e.target.closest("a, button, input, label, .dropdown")) return;
    location.href = row.dataset.href;
  });

  /* ---------- Toggle task completion ---------- */
  document.addEventListener("click", e => {
    const btn = e.target.closest(".task-check, [data-toggle-done]");
    if (!btn) return;
    e.preventDefault();
    const item = btn.closest("[data-task]");
    if (!item) return;
    const done = item.classList.toggle("is-done");
    item.dataset.status = done ? "done" : "open";
    btn.setAttribute("aria-pressed", done);

    // Update status label / button text on detail page
    $$("[data-status-label]").forEach(l => {
      l.className = "status" + (done ? " status-done" : "");
      l.innerHTML = done
        ? '<i class="bi bi-check-circle-fill"></i> Выполнена'
        : '<i class="bi bi-circle"></i> В работе';
    });
    $$("[data-toggle-done]").forEach(b => {
      b.innerHTML = done
        ? '<i class="bi bi-arrow-counterclockwise me-1"></i>Вернуть в работу'
        : '<i class="bi bi-check2 me-1"></i>Отметить выполненной';
    });

    // Worker page: move task between "open" and "done" lists
    const target = $(done ? "#list-done" : "#list-open");
    if (target && item.parentElement !== target) {
      target.prepend(item);
      updateCounters();
    }
    applyFilters();
    toast(done ? "Задача отмечена выполненной" : "Задача возвращена в работу");
  });

  function updateCounters() {
    $$("[data-count-for]").forEach(c => {
      const list = $(c.dataset.countFor);
      if (!list) return;
      const n = $$("[data-task]", list).length;
      c.textContent = n;
      const empty = list.parentElement.querySelector(".empty");
      if (empty) empty.classList.toggle("d-none", n > 0);
    });
    const open = $("#list-open"), done = $("#list-done"), bar = $("#worker-progress");
    if (open && done && bar) {
      const o = $$("[data-task]", open).length, d = $$("[data-task]", done).length;
      const pct = o + d ? Math.round((d / (o + d)) * 100) : 0;
      bar.style.width = pct + "%";
      const lbl = $("#worker-progress-label");
      if (lbl) lbl.textContent = pct + "%";
    }
  }
  updateCounters();

  /* ---------- Search + filters for lists ---------- */
  const filterState = { q: "", status: "all", priority: "", type: "" };

  function applyFilters() {
    $$("[data-filterable]").forEach(container => {
      const items = $$("[data-task], [data-item]", container);
      let visible = 0;
      items.forEach(it => {
        const text = it.textContent.toLowerCase();
        const ok =
          (!filterState.q || text.includes(filterState.q)) &&
          (filterState.status === "all" || it.dataset.status === filterState.status) &&
          (!filterState.priority || it.dataset.priority === filterState.priority) &&
          (!filterState.type || it.dataset.type === filterState.type);
        it.classList.toggle("d-none", !ok);
        if (ok) visible++;
      });
      const empty = $(container.dataset.empty || "#__none");
      if (empty) empty.classList.toggle("d-none", visible > 0);
      const counter = $(container.dataset.counter || "#__none");
      if (counter) counter.textContent = visible;
    });
  }

  $$("[data-search]").forEach(inp =>
    inp.addEventListener("input", () => { filterState.q = inp.value.trim().toLowerCase(); applyFilters(); })
  );
  $$("[data-filter-status] .btn").forEach(btn =>
    btn.addEventListener("click", () => {
      $$(".btn", btn.parentElement).forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      filterState.status = btn.dataset.value;
      applyFilters();
    })
  );
  $$("[data-filter-priority]").forEach(sel =>
    sel.addEventListener("change", () => { filterState.priority = sel.value; applyFilters(); })
  );
  $$("[data-filter-type]").forEach(sel =>
    sel.addEventListener("change", () => { filterState.type = sel.value; applyFilters(); })
  );

  // "/" focuses search
  document.addEventListener("keydown", e => {
    if (e.key === "/" && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) {
      const s = $("[data-search]");
      if (s) { e.preventDefault(); s.focus(); }
    }
  });

  /* ---------- Delete confirmation modal ---------- */
  const delModal = $("#confirmDelete");
  if (delModal) {
    delModal.addEventListener("show.bs.modal", e => {
      const trigger = e.relatedTarget;
      $("[data-delete-name]", delModal).textContent = trigger?.dataset.name || "этот объект";
      delModal._row = trigger?.closest("[data-item], [data-task]");
    });
    $("[data-delete-confirm]", delModal).addEventListener("click", () => {
      const row = delModal._row;
      bootstrap.Modal.getInstance(delModal).hide();
      if (row) { row.remove(); applyFilters(); updateCounters(); }
      toast("Удалено");
      const redirect = delModal.dataset.redirect;
      if (!row && redirect) setTimeout(() => (location.href = redirect), 600);
    });
  }

  /* ---------- Inline add (positions / task types / tags) ---------- */
  $$("form[data-inline-add]").forEach(form => {
    form.addEventListener("submit", e => {
      e.preventDefault();
      const input = $("input", form);
      const name = input.value.trim();
      if (!name) { input.focus(); return; }
      const list = $(form.dataset.inlineAdd);
      const tpl = $("template", list.parentElement);
      const node = tpl.content.firstElementChild.cloneNode(true);
      node.innerHTML = node.innerHTML.replaceAll("__NAME__", name);
      list.prepend(node);
      input.value = "";
      $(".empty", list.parentElement)?.classList.add("d-none");
      toast(`«${name}» добавлено`);
    });
  });

  /* ---------- Inline rename ---------- */
  document.addEventListener("click", e => {
    const btn = e.target.closest("[data-rename]");
    if (!btn) return;
    const row = btn.closest("[data-item]");
    const nameEl = $(".item-name", row);
    const old = nameEl.textContent;
    const input = document.createElement("input");
    input.className = "form-control form-control-sm";
    input.style.maxWidth = "280px";
    input.value = old;
    nameEl.replaceWith(input);
    input.focus(); input.select();
    const finish = save => {
      const span = document.createElement(nameEl.tagName.toLowerCase());
      span.className = nameEl.className;
      if (nameEl.getAttribute("href")) span.setAttribute("href", nameEl.getAttribute("href"));
      span.textContent = save && input.value.trim() ? input.value.trim() : old;
      input.replaceWith(span);
      if (save && span.textContent !== old) toast("Сохранено");
    };
    input.addEventListener("keydown", ev => {
      if (ev.key === "Enter") finish(true);
      if (ev.key === "Escape") finish(false);
    });
    input.addEventListener("blur", () => input.isConnected && finish(true));
  });

  /* ---------- Tag input (task form) ---------- */
  $$("[data-tag-input]").forEach(wrap => {
    const input = $("input[type=text]", wrap);
    const box = $(".tag-box", wrap);
    const hidden = $("input[type=hidden]", wrap);
    const sync = () => (hidden.value = $$(".tag", box).map(t => t.dataset.value).join(","));
    const add = raw => {
      const v = raw.trim().toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9а-я_-]/gi, "");
      if (!v || $$(".tag", box).some(t => t.dataset.value === v)) return;
      const t = document.createElement("span");
      t.className = "tag"; t.dataset.value = v;
      t.innerHTML = `#${v} <i class="bi bi-x remove" role="button" aria-label="Убрать"></i>`;
      box.appendChild(t); sync();
    };
    input.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === ",") { e.preventDefault(); add(input.value); input.value = ""; }
      if (e.key === "Backspace" && !input.value) { $$(".tag", box).pop()?.remove(); sync(); }
    });
    input.addEventListener("change", () => { if (input.value) { add(input.value); input.value = ""; } });
    box.addEventListener("click", e => { if (e.target.closest(".remove")) { e.target.closest(".tag").remove(); sync(); } });
    $$("[data-suggest]", wrap).forEach(s => s.addEventListener("click", () => add(s.dataset.suggest)));
    sync();
  });

  /* ---------- Assignee picker: live counter ---------- */
  $$("[data-assignees]").forEach(box => {
    const out = $(box.dataset.assignees);
    const upd = () => (out.textContent = $$("input:checked", box).length);
    box.addEventListener("change", upd); upd();
    const filter = $("[data-assignee-search]");
    filter?.addEventListener("input", () => {
      const q = filter.value.toLowerCase();
      $$(".form-check", box).forEach(r => r.classList.toggle("d-none", !r.textContent.toLowerCase().includes(q)));
    });
  });

  /* ---------- Bootstrap validation ---------- */
  $$("form.needs-validation").forEach(form =>
    form.addEventListener("submit", e => {
      if (!form.checkValidity()) { e.preventDefault(); e.stopPropagation(); }
      else if (form.dataset.demo !== undefined) {
        e.preventDefault();
        toast("Сохранено (демо)");
        if (form.dataset.redirect) setTimeout(() => (location.href = form.dataset.redirect), 700);
      }
      form.classList.add("was-validated");
    })
  );

  /* ---------- Deadline highlighting ---------- */
  const today = new Date(document.body.dataset.today || Date.now());
  $$("[data-deadline]").forEach(el => {
    const d = new Date(el.dataset.deadline);
    const item = el.closest("[data-task]");
    if (d < today && !(item && item.classList.contains("is-done"))) {
      el.classList.add("overdue");
      el.title = "Просрочено";
    }
  });

  /* ---------- Password visibility ---------- */
  $$("[data-toggle-password]").forEach(btn =>
    btn.addEventListener("click", () => {
      const inp = $(btn.dataset.togglePassword);
      const show = inp.type === "password";
      inp.type = show ? "text" : "password";
      btn.innerHTML = `<i class="bi bi-eye${show ? "-slash" : ""}"></i>`;
    })
  );

  applyFilters();
})();
