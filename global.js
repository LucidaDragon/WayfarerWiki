"use strict";

addEventListener("DOMContentLoaded", () =>
{
	function header_depth(header)
	{
		switch (header.tagName.toLowerCase())
		{
			case "h1": return 1;
			case "h2": return 2;
			case "h3": return 3;
			case "h4": return 4;
			case "h5": return 5;
			case "h6": return 6;
			default: return 0;
		}
	}

	const toc = document.createElement("table");
	toc.classList.add("toc");
	const index = [0, 0, 0, 0, 0, 0];
	document.querySelectorAll("h2, h3, h4, h5, h6").forEach((header) =>
	{
		const depth = header_depth(header) - 1;
		index[depth - 1] += 1;
		for (let i = depth; i < index.length; i++) index[i] = 0;
		const id = index.slice(0, depth).join(".");
		const link = document.createElement("a");
		const cell = document.createElement("td");
		const row = document.createElement("tr");
		link.textContent = `${id}. ${header.textContent}`;
		link.href = `#${id}`;
		header.id = id;
		cell.appendChild(link);
		row.appendChild(cell);
		toc.appendChild(row);
	});

	const start = document.querySelectorAll("hr")[0];
	(start ? start : document.body.firstChild).after(toc);
});