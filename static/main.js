// DOM Elements
const input = document.querySelector("#artist_input");
const btn = document.querySelector("#submit_btn");
const blind_box = document.querySelector("#blind_box_btn");
const result_box = document.querySelector("#result_box");

// Submit artist to backend
btn.addEventListener("click", () => {
    const name = input.value.trim();
    if (!name) {
        alert("Please enter an artist name.");
        return;
    }

    fetch("http://127.0.0.1:5000/artists", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ artist_name: name })
    })
    .then(res => res.json())
    .then(data => {
        if (data.message) {
            load_artists();
        } else if (data.error) {
            alert("Error: " + data.error);
        }
    })
    .catch(err => {
        console.error("Request failed:", err);
        alert("Something went wrong.");
    });
});

// Load artist info + top tracks
function load_artists() {
    fetch("http://127.0.0.1:5000/artists")
    .then(res => res.json())
    .then(data => {
        const container = document.querySelector("#artist_list");
        container.innerHTML = "";

        data.forEach(artist => {
            const item = document.createElement("div");
            item.className = "artist";

            const info = document.createElement("p");
            info.textContent = `${artist.name} - ${artist.num_albums} albums - Popularity: ${artist.popularity}`;
            item.appendChild(info);

            const trackList = document.createElement("ul");
            artist.top_tracks.split(",").forEach(track => {
                const li = document.createElement("li");
                li.textContent = track.trim();
                trackList.appendChild(li);
            });
            item.appendChild(trackList);

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.textContent = "Delete";
            deleteBtn.addEventListener("click", () => {
                fetch(`http://127.0.0.1:5000/artists/${encodeURIComponent(artist.name)}`, {
                    method: "DELETE"
                })
                .then(res => res.json())
                .then(() => load_artists())
                .catch(err => console.error("Failed to delete artist:", err));
            });

            item.appendChild(deleteBtn);
            container.appendChild(item);
        });
    });
}

// Blind box animation and save handling
blind_box.addEventListener("click", () => {
    const artist = input.value.trim();
    if (!artist) {
        alert("Please enter an artist name.");
        return;
    }

    fetch(`http://127.0.0.1:5000/blindbox/${encodeURIComponent(artist)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        result_box.innerHTML = "";  // Clear previous results

        // Create each card with staggered animation
        data.box_results.forEach((t, i) => {
            const card = document.createElement("div");
            card.className = `flip-card ${t.rarity.toLowerCase()} hidden-card`; // start hidden
        
            const inner = document.createElement("div");
            inner.className = "flip-card-inner";
        
            const front = document.createElement("div");
            front.className = "flip-card-front";
        
            if (t.album_image) {
                const img = document.createElement("img");
                img.src = t.album_image;
                img.alt = "Album cover";
                img.className = "album-art";
                front.appendChild(img);
            }
        
            const back = document.createElement("div");
            back.className = "flip-card-back";
        
            const title = document.createElement("p");
            title.innerHTML = `<strong>${t.track}</strong>`;
            back.appendChild(title);
        
            const rarityTag = document.createElement("p");
            rarityTag.className = t.rarity.toLowerCase();
            rarityTag.textContent = t.rarity;
            back.appendChild(rarityTag);
        
            if (t.preview_url) {
                const audio = document.createElement("audio");
                audio.controls = true;
                audio.src = t.preview_url;
                back.appendChild(audio);
            }
        
            const saveBtn = document.createElement("button");
            saveBtn.className = "save-btn";
            saveBtn.textContent = "Save";
            saveBtn.dataset.track = t.track;
            saveBtn.dataset.rarity = t.rarity;
            saveBtn.dataset.preview = t.preview_url || "";
            saveBtn.dataset.image = t.album_image || "";
            back.appendChild(saveBtn);
        
            inner.appendChild(front);
            inner.appendChild(back);
            card.appendChild(inner);
        
            result_box.appendChild(card); // ✅ Only append once, after it's fully built
        
            // Animation + click listener after DOM paint
            setTimeout(() => {
                card.classList.remove("hidden-card");
                card.style.animation = "dropIn 0.6s ease-out forwards";
                card.style.animationDelay = `${i * 150}ms`;
        
                // ✅ Flip behavior
                card.addEventListener("click", () => {
                    inner.classList.toggle("flipped");
                });
            }, 50);
        });

        // Save behavior
        document.querySelectorAll(".save-btn").forEach(btn => {
            btn.addEventListener("click", e => {
                e.stopPropagation();

                // Build save object
                const trackData = {
                    track: btn.dataset.track,
                    rarity: btn.dataset.rarity,
                    preview_url: btn.dataset.preview,
                    album_image: btn.dataset.image
                };

                // POST to /inventory
                fetch("/inventory", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(trackData)
                })
                .then(res => {
                    if (!res.ok) return res.json().then(err => { throw err });
                    return res.json();
                })
                .then(data => {
                    alert(data.message);
                    loadInventory();
                })
                .catch(err => {
                    console.error("Save failed:", err);
                    alert(err.error || "Failed to save card.");
                });
            });
        });
    })
    .catch(err => {
        console.error("Blind box failed:", err);
        alert("Something went wrong.");
    });
});

// Inventory loader
function loadInventory() {
    fetch("/inventory")
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById("inventory_list");
        if (data.length === 0) {
            container.innerHTML = "<p>No cards saved yet.</p>";
            return;
        }

        container.innerHTML = data.map(card => `
            <div class="inventory-card">
              <div class="track-card ${card.rarity.toLowerCase()}">
                <p><strong>${card.track}</strong> - ${card.rarity}</p>
                ${card.album_image ? `<img src="${card.album_image}" alt="cover">` : ""}
              </div>
              <button class="delete-btn" data-track="${card.track}">Remove</button>
            </div>
          `).join("");       

        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const track = btn.dataset.track;
        
                fetch("/inventory", {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ track })
                })
                .then(res => {
                    if (!res.ok) {
                        // Try to read error response; if fail, throw generic one
                        return res.json()
                            .then(err => { throw err; })
                            .catch(() => { throw { error: "Unexpected server response." }; });
                    }
                    return res.json();
                })
                .then(data => {
                    // ✅ Optional: log or toast if you want
                    console.log(data.message);
                    loadInventory();  // refresh UI
                })
                .catch(err => {
                    // ✅ Silent failure: no popup, just log and reload
                    console.warn("Delete failed or skipped:", err);
                    loadInventory();  // still refresh even if something failed
                });
            });
        });
        
        
    });
}

// Initial render
load_artists();
loadInventory();
