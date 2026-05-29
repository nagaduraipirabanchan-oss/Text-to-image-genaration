// 1. LOGIN AUTHENTICATION LOGIC (With 3D Shake & Opacity Fix)
function checkLogin() {
    const user = document.getElementById('username').value.trim();
    const pass = document.getElementById('password').value.trim();
    const errorMsg = document.getElementById('login-error');

    // Mukhayamaana Fix: Username/Password check
    if(user === "admin" && pass === "admin123") {
        document.getElementById('login-overlay').style.opacity = '0';
        setTimeout(() => {
            document.getElementById('login-overlay').classList.add('hidden');
            document.getElementById('main-app').classList.remove('hidden');
        }, 500);
        localStorage.setItem('imaginix_auth', 'true');
        updateStats();
    } else {
        errorMsg.classList.remove('hidden');
        // Vibration or Shake effect function call
        const loginBox = document.querySelector('.glass');
        if(loginBox) {
            loginBox.classList.add('animate-shake');
            setTimeout(() => loginBox.classList.remove('animate-shake'), 500);
        }
    }
}

// 2. TAB MANAGEMENT
function showTab(id) {
    // Hide all sections
    document.querySelectorAll('.tab-content').forEach(section => {
        section.classList.add('hidden');
        section.classList.remove('block');
    });

    // Show the targeted section
    const activeSection = document.getElementById(id);
    if(activeSection) {
        activeSection.classList.remove('hidden');
        activeSection.classList.add('block');
    }

    // Update Navbar button styles
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('text-cyan-400', 'bg-white/5', 'border', 'border-white/10');
        link.classList.add('text-gray-400');
    });
    
    const activeLink = document.getElementById('nav-' + id);
    if(activeLink) {
        activeLink.classList.add('text-cyan-400', 'bg-white/5', 'border', 'border-white/10');
    }

    if(id === 'gallery') loadGallery();
    if(id === 'home') updateStats();
}

// 3. 404 OIL PAINTING FIX: HTML and JS match
function fillPrompt(text, style) {
    document.getElementById('prompt').value = text;
    // Indha style value exact-ah HTML select option-oda value-ku match aaganum
    document.getElementById('style').value = style; 
}

// 4. GENERATE IMAGE LOGIC
async function generate() {
    const prompt = document.getElementById('prompt').value;
    const style = document.getElementById('style').value;
    const resValue = document.getElementById('resolution').value;
    const btn = document.getElementById('gen-btn');
    const icon = document.getElementById('btn-icon');

    if(!prompt) return alert("Please type something first!");

    // UI Updates
    btn.disabled = true;
    if(icon) icon.classList.add('fa-spin');
    document.getElementById('loader').classList.remove('hidden');
    document.getElementById('placeholder').classList.add('hidden');
    document.getElementById('res-img').classList.add('hidden');
    document.getElementById('download-overlay').classList.add('hidden');

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ prompt, style, resolution: resValue })
        });
        const data = await response.json();
        if(data.success) {
            const img = document.getElementById('res-img');
            img.src = data.img;
            img.classList.remove('hidden');
            document.getElementById('download-link').href = data.img;
            document.getElementById('download-overlay').classList.remove('hidden');
        } else { 
            alert("Server Error: " + data.error); 
            document.getElementById('placeholder').classList.remove('hidden');
        }
    } catch(e) { 
        alert("Check server connection!"); 
        document.getElementById('placeholder').classList.remove('hidden');
    } finally {
        document.getElementById('loader').classList.add('hidden');
        btn.disabled = false;
        if(icon) icon.classList.remove('fa-spin');
    }
}

// 5. PERSISTENT LOGIN CHECK ON LOAD
window.onload = function() {
    if(localStorage.getItem('imaginix_auth') === 'true') {
        const loginOverlay = document.getElementById('login-overlay');
        const mainApp = document.getElementById('main-app');
        if(loginOverlay) loginOverlay.classList.add('hidden');
        if(mainApp) mainApp.classList.remove('hidden');
        updateStats();
    }
};

// 6. STATS LOGIC
async function updateStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        const display = document.getElementById('stat-total-display');
        if(display) {
            display.innerText = (12540 + data.total).toLocaleString() + "+";
        }
    } catch(e) { console.log("Stats error"); }
}

// 7. GALLERY LOADER
async function loadGallery() {
    const grid = document.getElementById('gallery-grid');
    if(!grid) return;
    grid.innerHTML = '<p class="col-span-full animate-pulse text-cyan-400">Accessing Data...</p>';
    
    try {
        const res = await fetch('/api/gallery');
        const items = await res.json();
        
        if(items.length === 0) {
            grid.innerHTML = '<p class="col-span-full text-gray-500">No artworks in gallery yet.</p>';
            return;
        }

        grid.innerHTML = items.map(item => `
            <div class="glass p-3 rounded-2xl border border-white/10 group overflow-hidden neon-hover">
                <div class="h-56 overflow-hidden rounded-xl">
                    <img src="${item.image_path}" class="w-full h-full object-cover group-hover:scale-110 transition duration-500" onerror="this.src='https://via.placeholder.com/300x400/050816/cyan?text=AI+Art'">
                </div>
                <div class="mt-3 text-left">
                    <p class="text-xs font-bold truncate text-white">${item.prompt}</p>
                    <p class="text-[10px] text-cyan-400 mt-1 uppercase tracking-tighter">${item.model || 'Stable Diffusion'}</p>
                </div>
            </div>
        `).join('');
    } catch(e) { grid.innerHTML = "Error loading gallery."; }
}