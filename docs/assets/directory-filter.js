document.querySelectorAll("[data-directory-filter]").forEach((input) => {
  const table = document.querySelector("[data-directory-table]");
  const count = document.querySelector("#directory-count");
  if (!table || !count) return;

  const rows = [...table.querySelectorAll("tbody tr")];
  const update = () => {
    const query = input.value.trim().toLocaleLowerCase();
    let visible = 0;
    rows.forEach((row) => {
      const matches = !query || row.dataset.search.includes(query);
      row.hidden = !matches;
      if (matches) visible += 1;
    });
    count.textContent = document.documentElement.lang === "zh-CN"
      ? `显示 ${visible} / ${rows.length} 条记录`
      : `${visible} of ${rows.length} entries shown`;
  };

  input.addEventListener("input", update);
  update();
});
