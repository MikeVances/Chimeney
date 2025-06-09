document.getElementById("search-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const form = e.target;
    const typeMap = {
      "вытяжная": "VBV",
      "приточная активная": "VBA",
      "приточная пассивная": "VBP",
      "приточная с подмешиванием": "VBR"
    };
    const rawType = form["тип"].value.trim().toLowerCase();
    const data = {
      тип: typeMap[rawType] || rawType,
      диаметр: form["диаметр"].value,
      клапан: form["клапан"]?.value,
    };
  
    const response = await fetch("/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data),
    });
  
    const result = await response.json();
    const container = document.getElementById("results");
    container.innerHTML = "";
  
    const output = Array.isArray(result) ? result : result.results;

    if (output?.length) {
      const list = document.createElement("ul");
      output.forEach(item => {
        const li = document.createElement("li");
        li.textContent = `${item.artikul}: ${item.name} — ${item.price}`;
        list.appendChild(li);
      });
      container.appendChild(list);
    } else {
      container.textContent = result.message || "Ничего не найдено.";
    }
  });


const motorOptions = document.getElementById("motor-options");

function checkAndShowAdvanced() {
  const typeField = document.querySelector('select[name="тип"]');
  const advancedOptions = document.getElementById("advanced-options");
  if (!typeField || !advancedOptions) return;

  const activeTypes = ["вытяжная", "приточная активная"];
  const showMotorFields = activeTypes.includes(typeField.value.toLowerCase());

  if (typeField.value === "приточная активная" || typeField.value === "вытяжная") {
    advancedOptions.style.display = "block";
    const motorField = document.getElementById("motor-fields");
    if (motorField) {
      motorField.style.display = showMotorFields ? "block" : "none";
    }
  } else {
    advancedOptions.style.display = "none";
    const motorField = document.getElementById("motor-fields");
    if (motorField) {
      motorField.style.display = "none";
    }
  }
}

document.getElementById("тип").addEventListener("change", checkAndShowAdvanced);
checkAndShowAdvanced();